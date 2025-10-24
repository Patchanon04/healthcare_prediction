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
from django.contrib.auth import authenticate
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .models import Transaction, UserProfile
from .serializers import (
    TransactionSerializer,
    UploadImageSerializer,
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
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
    patient_name = serializer.validated_data['patient_name']
    age = serializer.validated_data['age']
    gender = serializer.validated_data['gender']
    mrn = serializer.validated_data['mrn']
    phone = serializer.validated_data.get('phone', '')
    
    try:
        # Upload to S3 or local storage
        file_name = f"dog_images/{int(time.time())}_{image_file.name}"
        saved_path = default_storage.save(file_name, image_file)
        
        # Generate full URL
        if settings.USE_S3:
            image_url = f"{settings.MEDIA_URL}{saved_path}"
        else:
            # For local storage, use a mock URL
            image_url = f"http://backend:8000{settings.MEDIA_URL}{saved_path}"
        
        logger.info(f"Image uploaded to: {image_url}")
        
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
            image_url=image_url,
            diagnosis=ml_diagnosis,
            confidence=ml_confidence,
            model_version=ml_model_version,
            processing_time=ml_processing_time,
            patient_name=patient_name,
            age=age,
            gender=gender,
            mrn=mrn,
            phone=phone,
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


# Authentication Endpoints
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # Create user profile
        UserProfile.objects.create(user=user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
        }, status=status.HTTP_201_CREATED)
    return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
    return Response({'token': token.key, 'username': user.username, 'email': user.email})


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
