"""
API views for medical diagnosis predictions.
"""
import time
import os
import logging
import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.db import connection
from django.db.models import Q, Count, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Transaction, UserProfile, Patient, ChatRoom, Message, TreatmentPlan, Medication, FollowUpNote
from .serializers import (
    TransactionSerializer,
    UploadImageSerializer,
    LoginSerializer,
    UserProfileSerializer,
    ChatRoomSerializer,
    MessageSerializer,
    UserBasicSerializer,
    PatientSerializer,
    TreatmentPlanSerializer,
    MedicationSerializer,
    FollowUpNoteSerializer,
)

logger = logging.getLogger(__name__)


class DefaultPagination(PageNumberPagination):
    """
    Custom pagination class with configurable page size.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@retry(
    stop=stop_after_attempt(settings.ML_SERVICE_MAX_RETRIES),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout))
)
def call_ml_service(image_url: str) -> dict:
    """
    Call ML microservice for prediction with retry logic.
    
    Args:
        image_url: URL of the image to predict
        
    Returns:
        dict: Prediction response from ML service
        
    Raises:
        requests.RequestException: If all retry attempts fail
    """
    ml_service_url = f"{settings.ML_SERVICE_URL}/predict/"
    
    try:
        response = requests.post(
            ml_service_url,
            json={"image_url": image_url},
            timeout=settings.ML_SERVICE_TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"ML service error: {str(e)}")
        raise


@api_view(['POST'])
def upload_image(request):
    """
    Upload image endpoint.
    
    POST /api/v1/upload/
    
    Accepts an image file, uploads it to S3, calls ML service for prediction,
    and saves the result to the database.
    """
    start_time = time.time()
    
    # Validate input
    serializer = UploadImageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": "Invalid image data", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image_file = serializer.validated_data['image']
    patient_id = serializer.validated_data.get('patient_id')
    # Legacy fields used only to create/find Patient when patient_id is not provided
    patient_name = serializer.validated_data.get('patient_name')
    age = serializer.validated_data.get('age')
    gender = serializer.validated_data.get('gender')
    mrn = serializer.validated_data.get('mrn')
    phone = serializer.validated_data.get('phone', '')
    
    try:
        # Upload to S3 or local storage
        file_name = f"patient_images/{int(time.time())}_{image_file.name}"
        saved_path = default_storage.save(file_name, image_file)
        
        # Generate full URL
        if settings.USE_S3:
            image_url = f"{settings.MEDIA_URL}{saved_path}"
        else:
            # For local storage, use a publicly accessible URL
            # ML service needs to access this via HTTP
            image_url = f"http://medml_backend:8000{settings.MEDIA_URL}{saved_path}"
        
        logger.info(f"Image uploaded to: {image_url}")
        
        # Resolve patient record
        patient_obj = None
        if patient_id:
            try:
                patient_obj = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return Response({"error": "Patient not found"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Create or get patient by MRN if provided; fallback by name+phone
            if mrn:
                patient_obj, _ = Patient.objects.get_or_create(
                    mrn=mrn,
                    defaults={
                        'full_name': patient_name,
                        'age': age,
                        'gender': gender,
                        'phone': phone or '',
                    }
                )
                # If exists but missing data, update minimally
                updated = False
                if patient_name and not patient_obj.full_name:
                    patient_obj.full_name = patient_name; updated = True
                if age is not None and patient_obj.age != age:
                    patient_obj.age = age; updated = True
                if gender and patient_obj.gender != gender:
                    patient_obj.gender = gender; updated = True
                if phone and not patient_obj.phone:
                    patient_obj.phone = phone; updated = True
                if updated:
                    patient_obj.save()
            else:
                # No MRN, try name+phone grouping
                patient_obj, _ = Patient.objects.get_or_create(
                    full_name=patient_name,
                    phone=phone or '',
                    defaults={
                        'mrn': '',
                        'age': age,
                        'gender': gender,
                    }
                )

        # Call ML service for prediction
        try:
            prediction_result = call_ml_service(image_url)
        except requests.RequestException as e:
            return Response(
                {"error": "ML service unavailable", "details": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Map ML response to our schema
        ml_diagnosis = prediction_result.get('diagnosis') or prediction_result.get('breed')
        ml_confidence = prediction_result.get('confidence')
        ml_model_version = prediction_result.get('model_version')
        ml_processing_time = prediction_result.get('processing_time')

        # Save transaction to database
        transaction = Transaction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            patient=patient_obj,
            image_url=image_url,
            diagnosis=ml_diagnosis,
            confidence=ml_confidence,
            model_version=ml_model_version,
            processing_time=ml_processing_time,
        )
        
        total_time = round(time.time() - start_time, 2)
        logger.info(f"Transaction {transaction.id} completed in {total_time}s")
        
        # Return response
        response_data = TransactionSerializer(transaction).data
        response_data['total_processing_time'] = total_time
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return Response(
            {"error": "Internal server error", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class TransactionHistoryView(generics.ListAPIView):
    """
    Get paginated transaction history filtered by current user.
    
    GET /api/v1/history/
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Number of items per page (default: 10, max: 100)
    """
    serializer_class = TransactionSerializer
    pagination_class = DefaultPagination
    
    def get_queryset(self):
        # Filter transactions by current user
        if self.request.user.is_authenticated:
            return Transaction.objects.filter(user=self.request.user).order_by('-uploaded_at')
        return Transaction.objects.none()


class TransactionDetailView(generics.RetrieveAPIView):
    """Retrieve a single transaction by id."""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint."""
    return Response({'status': 'ok'})


class PatientListCreateView(generics.ListCreateAPIView):
    """
    List patients with search, or create a new patient.
    GET /api/v1/patients/?search=...
    POST /api/v1/patients/
    """
    serializer_class = PatientSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        # Filter patients by current user
        qs = Patient.objects.filter(created_by=self.request.user).order_by('-created_at')
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(full_name__icontains=search) |
                Q(mrn__icontains=search) |
                Q(phone__icontains=search)
            )
        return qs
    
    def perform_create(self, serializer):
        """Set created_by to current user when creating patient."""
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a patient by id."""
    serializer_class = PatientSerializer
    
    def get_queryset(self):
        """Only allow access to own patients."""
        return Patient.objects.filter(created_by=self.request.user)


class PatientTransactionsView(generics.ListAPIView):
    """
    List transactions for a specific patient.
    GET /api/v1/patients/<int:patient_id>/transactions/
    """
    serializer_class = TransactionSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        return Transaction.objects.filter(patient_id=patient_id).order_by('-uploaded_at')


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def seed_accounts(request):
    """
    Seed database with test accounts.
    POST /api/v1/seed-accounts/
    
    Body (optional):
    {
        "reset": true
    }
    """
    from django.contrib.auth.models import User
    
    reset = request.data.get('reset', False)
    
    accounts = [
        {
            'username': 'doctor1',
            'password': 'password123',
            'email': 'doctor1@hospital.com',
            'full_name': 'Dr. John Smith',
            'contact': '081-234-5678',
            'role': 'doctor'
        },
        {
            'username': 'nurse1',
            'password': 'password123',
            'email': 'nurse1@hospital.com',
            'full_name': 'Nurse Jane Doe',
            'contact': '082-345-6789',
            'role': 'nurse'
        },
        {
            'username': 'admin1',
            'password': 'password123',
            'email': 'admin1@hospital.com',
            'full_name': 'Admin User',
            'contact': '083-456-7890',
            'role': 'admin'
        },
        {
            'username': 'radiologist1',
            'password': 'password123',
            'email': 'radiologist1@hospital.com',
            'full_name': 'Dr. Sarah Johnson',
            'contact': '084-567-8901',
            'role': 'radiologist'
        },
    ]
    
    # Reset if requested
    if reset:
        deleted_count = User.objects.filter(username__in=[a['username'] for a in accounts]).delete()[0]
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} existing accounts")
    
    created = []
    skipped = []
    
    for account in accounts:
        # Check if user already exists
        if User.objects.filter(username=account['username']).exists():
            skipped.append(account['username'])
            continue
        
        # Create user
        user = User.objects.create_user(
            username=account['username'],
            password=account['password'],
            email=account['email']
        )
        
        # Create profile
        UserProfile.objects.create(
            user=user,
            full_name=account['full_name'],
            contact=account['contact'],
            role=account['role']
        )
        
        created.append({
            'username': account['username'],
            'role': account['role'],
            'email': account['email']
        })
    
    return Response({
        'success': True,
        'created': len(created),
        'skipped': len(skipped),
        'accounts': created,
        'skipped_usernames': skipped,
        'message': f'Created {len(created)} accounts, skipped {len(skipped)} existing accounts'
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
    if not user:
        return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    })


@api_view(['GET'])
def me(request):
    user = request.user
    return Response({'username': user.username, 'email': user.email})


@api_view(['GET', 'PUT'])
def profile(request):
    """
    Get or update user profile.
    """
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@cache_page(60)  # cache for 60 seconds
def metrics_summary(request):
    """Return quick summary numbers for dashboard."""
    today = timezone.localdate()
    total_patients = Patient.objects.count()
    total_predictions = Transaction.objects.count()
    today_predictions = Transaction.objects.filter(uploaded_at__date=today).count()
    avg_conf = Transaction.objects.aggregate(avg=Avg('confidence'))['avg'] or 0
    return Response({
        'total_patients': total_patients,
        'total_predictions': total_predictions,
        'today_predictions': today_predictions,
        'avg_confidence': avg_conf,
        'date': str(today),
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@cache_page(60)
def metrics_daily(request):
    """Return counts per day for the last N days (default 14)."""
    try:
        days = int(request.query_params.get('days', 14))
    except (TypeError, ValueError):
        days = 14
    days = max(1, min(days, 60))
    start = timezone.now() - timezone.timedelta(days=days - 1)
    qs = (
        Transaction.objects
        .filter(uploaded_at__date__gte=start.date())
        .annotate(day=TruncDate('uploaded_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    data = [{'date': str(row['day']), 'count': row['count']} for row in qs]
    return Response({'series': data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@cache_page(60)
def metrics_diagnosis_distribution(request):
    """Return diagnosis distribution for doughnut chart."""
    qs = (
        Transaction.objects
        .exclude(diagnosis__isnull=True)
        .exclude(diagnosis='')
        .values('diagnosis')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    data = [{'diagnosis': row['diagnosis'], 'count': row['count']} for row in qs]
    return Response({'distribution': data})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def reports_summary(request):
    """
    Generate comprehensive report data for a date range.
    GET /api/v1/reports/summary/?start=YYYY-MM-DD&end=YYYY-MM-DD
    
    Returns:
    - summary: total_patients, total_predictions, avg_confidence
    - daily_series: count per day
    - diagnosis_distribution: breakdown by diagnosis
    - recent_transactions: sample transactions (max 100)
    """
    from datetime import datetime, timedelta
    
    # Parse date range
    start_str = request.query_params.get('start')
    end_str = request.query_params.get('end')
    
    try:
        if start_str and end_str:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
        else:
            # Default: last 14 days
            end_date = timezone.localdate()
            start_date = end_date - timedelta(days=13)
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate range
    if start_date > end_date:
        return Response({'error': 'start date must be before end date'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Filter transactions by date range AND current user
    transactions_qs = Transaction.objects.filter(
        user=request.user,
        uploaded_at__date__gte=start_date,
        uploaded_at__date__lte=end_date
    )
    
    # Summary stats
    total_predictions = transactions_qs.count()
    avg_confidence = transactions_qs.aggregate(avg=Avg('confidence'))['avg'] or 0
    
    # Count patients created by current user
    total_patients = Patient.objects.filter(created_by=request.user).count()
    
    # Count unique patients WITH transactions in this range (for reference)
    patients_with_predictions = transactions_qs.values('patient').distinct().count()
    
    # Daily series
    daily_qs = (
        transactions_qs
        .annotate(day=TruncDate('uploaded_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    daily_series = [{'date': str(row['day']), 'count': row['count']} for row in daily_qs]
    
    # Diagnosis distribution
    diagnosis_qs = (
        transactions_qs
        .exclude(diagnosis__isnull=True)
        .exclude(diagnosis='')
        .values('diagnosis')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    diagnosis_distribution = [{'diagnosis': row['diagnosis'], 'count': row['count']} for row in diagnosis_qs]
    
    # Recent transactions (max 100 for PDF)
    recent_transactions = transactions_qs.order_by('-uploaded_at')[:100]
    transactions_data = []
    for txn in recent_transactions:
        transactions_data.append({
            'id': str(txn.id),
            'uploaded_at': txn.uploaded_at.isoformat(),
            'patient_name': txn.patient.full_name if txn.patient else 'N/A',
            'patient_mrn': txn.patient.mrn if txn.patient else 'N/A',
            'diagnosis': txn.diagnosis,
            'confidence': round(txn.confidence, 2),
            'model_version': txn.model_version,
        })
    
    return Response({
        'date_range': {
            'start': str(start_date),
            'end': str(end_date),
        },
        'summary': {
            'total_patients': total_patients,
            'patients_with_predictions': patients_with_predictions,
            'total_predictions': total_predictions,
            'avg_confidence': round(avg_confidence, 2),
        },
        'daily_series': daily_series,
        'diagnosis_distribution': diagnosis_distribution,
        'recent_transactions': transactions_data,
    })


# ==================== Chat API Views ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_users(request):
    """List all users for chat (excluding current user)."""
    from django.contrib.auth.models import User
    users = User.objects.exclude(id=request.user.id).select_related('profile')
    serializer = UserBasicSerializer(users, many=True)
    return Response({'users': serializer.data})


class ChatRoomListCreateView(generics.ListCreateAPIView):
    """List chat rooms or create a new one."""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination
    
    def get_queryset(self):
        """Return rooms where user is a member."""
        return ChatRoom.objects.filter(members=self.request.user).prefetch_related('members', 'messages')
    
    def create(self, request, *args, **kwargs):
        """Create room or return existing chat with same members."""
        room_type = request.data.get('room_type', 'group')
        member_ids = request.data.get('member_ids', [])
        
        logger.info(f"📥 Received request: room_type={room_type}, member_ids={member_ids} (types: {[type(m).__name__ for m in member_ids]})")
        
        # Normalize all IDs to integers
        normalized_member_ids = []
        for mid in member_ids:
            try:
                normalized_member_ids.append(int(mid))
            except (ValueError, TypeError):
                logger.warning(f"⚠️ Could not normalize member_id: {mid} (type: {type(mid).__name__})")
                pass
        
        # All members including current user
        all_member_ids = set([request.user.id] + normalized_member_ids)
        expected_count = len(all_member_ids)
        
        logger.info(f"🔍 Creating {room_type} chat with normalized members: {all_member_ids} (count: {expected_count})")
        
        # Find existing chat with exact same members
        # Get all rooms where current user is a member
        candidate_rooms = ChatRoom.objects.filter(members=request.user).prefetch_related('members')
        
        logger.info(f"🔍 Found {candidate_rooms.count()} candidate rooms for user {request.user.id}")
        
        # Check each candidate room for exact member match
        for room in candidate_rooms:
            room_member_ids = set(room.members.values_list('id', flat=True))
            
            # Skip if member count doesn't match
            if len(room_member_ids) != expected_count:
                logger.info(f"⏭️ Skipping room {room.id}: member_count={len(room_member_ids)} != {expected_count}")
                continue
            
            logger.info(f"🔍 Checking room {room.id}: room_members={room_member_ids}, target={all_member_ids}, match={room_member_ids == all_member_ids}")
            
            if room_member_ids == all_member_ids:
                # For direct chat, also verify room_type
                if room_type == 'direct' and room.room_type != 'direct':
                    logger.info(f"⚠️ Room {room.id} has same members but wrong type: {room.room_type} != direct")
                    continue
                
                logger.info(f"✅ Chat with same members already exists: {room.id}")
                serializer = self.get_serializer(room)
                return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new room if not exists
        logger.info(f"❌ No existing chat found, creating new {room_type} room")
        return super().create(request, *args, **kwargs)


class ChatRoomDetailView(generics.RetrieveAPIView):
    """Get details of a specific chat room."""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only allow access to rooms where user is a member."""
        return ChatRoom.objects.filter(members=self.request.user).prefetch_related('members', 'messages')


class MessageListCreateView(generics.ListCreateAPIView):
    """List messages in a room or create a new message."""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination
    
    def get_queryset(self):
        """Return messages for a specific room."""
        room_id = self.kwargs.get('room_id')
        # Verify user is member of this room
        if not ChatRoom.objects.filter(id=room_id, members=self.request.user).exists():
            return Message.objects.none()
        return Message.objects.filter(room_id=room_id).select_related('sender', 'sender__profile')
    
    def perform_create(self, serializer):
        """Create message with current user as sender."""
        room_id = self.kwargs.get('room_id')
        room = ChatRoom.objects.get(id=room_id, members=self.request.user)
        serializer.save(sender=self.request.user, room=room)
        # Update room's updated_at
        room.save()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_messages_read(request, room_id):
    """Mark messages as read."""
    message_ids = request.data.get('message_ids', [])
    if not message_ids:
        return Response({'error': 'message_ids required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify user is member of room
    if not ChatRoom.objects.filter(id=room_id, members=request.user).exists():
        return Response({'error': 'Not a member of this room'}, status=status.HTTP_403_FORBIDDEN)
    
    messages = Message.objects.filter(id__in=message_ids, room_id=room_id)
    for msg in messages:
        msg.read_by.add(request.user)
    
    # Broadcast read receipts to the room via Channels so other clients update badges
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room_id}",
            {
                'type': 'messages_read',
                'user_id': request.user.id,
                'message_ids': [str(m.id) for m in messages],
            }
        )
    except Exception:
        # Non-fatal if channel layer is unavailable
        pass
    
    return Response({'status': 'success', 'marked_count': messages.count()})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_unread_count(request):
    """Get total unread message count for current user."""
    unread_count = Message.objects.filter(
        room__members=request.user
    ).exclude(
        read_by=request.user
    ).exclude(
        sender=request.user
    ).count()
    
    return Response({'unread_count': unread_count})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def global_search(request):
    """Global search across patients, diagnoses, and chat messages."""
    query = request.GET.get('q', '').strip()
    logger.info(f"Global search query: '{query}' by user {request.user.username}")
    
    if not query or len(query) < 2:
        return Response({
            'patients': [],
            'diagnoses': [],
            'messages': [],
            'total': 0
        })
    
    try:
        # Search patients
        patients = Patient.objects.filter(
            Q(full_name__icontains=query) |
            Q(mrn__icontains=query) |
            Q(phone__icontains=query)
        )[:10]
        logger.info(f"Found {patients.count()} patients")
        
        # Search diagnoses (transactions)
        diagnoses = Transaction.objects.filter(
            Q(diagnosis__icontains=query) |
            Q(patient__full_name__icontains=query) |
            Q(patient__mrn__icontains=query)
        ).select_related('patient').order_by('-uploaded_at')[:10]
        logger.info(f"Found {diagnoses.count()} diagnoses")
        
        # Search chat messages (only in rooms user is member of)
        messages = Message.objects.filter(
            room__members=request.user,
            content__icontains=query
        ).select_related('sender', 'room').order_by('-created_at')[:10]
        logger.info(f"Found {messages.count()} messages")
        
        # Serialize results
        from .serializers import PatientSerializer, TransactionSerializer
        
        patient_results = PatientSerializer(patients, many=True).data
        diagnosis_results = TransactionSerializer(diagnoses, many=True).data
        
        message_results = []
        for msg in messages:
            message_results.append({
                'id': str(msg.id),
                'content': msg.content,
                'sender': {
                    'id': msg.sender.id,
                    'username': msg.sender.username,
                    'full_name': getattr(msg.sender.profile, 'full_name', '') if hasattr(msg.sender, 'profile') else ''
                },
                'room_id': str(msg.room.id),
                'room_name': msg.room.name or 'Chat',
                'created_at': msg.created_at.isoformat()
            })
        
        total = len(patient_results) + len(diagnosis_results) + len(message_results)
        logger.info(f"Total results: {total}")
        
        return Response({
            'patients': patient_results,
            'diagnoses': diagnosis_results,
            'messages': message_results,
            'total': total,
            'query': query
        })
    except Exception as e:
        logger.error(f"Global search error: {str(e)}", exc_info=True)
        return Response({
            'patients': [],
            'diagnoses': [],
            'messages': [],
            'total': 0,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== Treatment Management API Views ====================

class TreatmentPlanListCreateView(generics.ListCreateAPIView):
    """List and create treatment plans for a patient."""
    serializer_class = TreatmentPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        return TreatmentPlan.objects.filter(patient_id=patient_id)
    
    def perform_create(self, serializer):
        patient_id = self.kwargs.get('patient_id')
        patient = Patient.objects.get(id=patient_id)
        serializer.save(patient=patient, created_by=self.request.user)


class TreatmentPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a treatment plan."""
    serializer_class = TreatmentPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        return TreatmentPlan.objects.filter(patient_id=patient_id)


class MedicationListCreateView(generics.ListCreateAPIView):
    """List and create medications for a patient."""
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        return Medication.objects.filter(patient_id=patient_id)
    
    def perform_create(self, serializer):
        patient_id = self.kwargs.get('patient_id')
        patient = Patient.objects.get(id=patient_id)
        serializer.save(patient=patient, prescribed_by=self.request.user)


class MedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a medication."""
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        return Medication.objects.filter(patient_id=patient_id)


class FollowUpNoteListCreateView(generics.ListCreateAPIView):
    """List and create follow-up notes for a patient."""
    serializer_class = FollowUpNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        return FollowUpNote.objects.filter(patient_id=patient_id)
    
    def perform_create(self, serializer):
        patient_id = self.kwargs.get('patient_id')
        patient = Patient.objects.get(id=patient_id)
        serializer.save(patient=patient, created_by=self.request.user)


class FollowUpNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a follow-up note."""
    serializer_class = FollowUpNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        return FollowUpNote.objects.filter(patient_id=patient_id)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def patient_timeline(request, patient_id):
    """
    Get complete timeline for a patient including:
    - Diagnoses (transactions)
    - Treatment plans
    - Medications
    - Follow-up notes
    """
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Gather all events
    events = []
    
    # Diagnoses
    from .serializers import TransactionSerializer, TreatmentPlanSerializer, MedicationSerializer, FollowUpNoteSerializer
    
    diagnoses = Transaction.objects.filter(patient=patient).order_by('-uploaded_at')
    for diag in diagnoses:
        events.append({
            'type': 'diagnosis',
            'date': diag.uploaded_at.isoformat(),
            'data': TransactionSerializer(diag).data
        })
    
    # Treatment plans
    treatments = TreatmentPlan.objects.filter(patient=patient).order_by('-start_date')
    for treatment in treatments:
        events.append({
            'type': 'treatment',
            'date': treatment.start_date.isoformat(),
            'data': TreatmentPlanSerializer(treatment).data
        })
    
    # Medications
    medications = Medication.objects.filter(patient=patient).order_by('-start_date')
    for med in medications:
        events.append({
            'type': 'medication',
            'date': med.start_date.isoformat(),
            'data': MedicationSerializer(med).data
        })
    
    # Follow-up notes
    notes = FollowUpNote.objects.filter(patient=patient).order_by('-created_at')
    for note in notes:
        events.append({
            'type': 'followup',
            'date': note.created_at.isoformat(),
            'data': FollowUpNoteSerializer(note).data
        })
    
    # Sort by date (newest first)
    events.sort(key=lambda x: x['date'], reverse=True)
    
    return Response({
        'patient_id': patient_id,
        'patient_name': patient.full_name,
        'events': events,
        'total': len(events)
    })
