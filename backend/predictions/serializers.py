"""
Serializers for medical diagnosis predictions API.
"""
from rest_framework import serializers
from .models import Transaction, UserProfile, Patient, ChatRoom, Message, TreatmentPlan, Medication, FollowUpNote
from django.contrib.auth.models import User


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    """
    patient = serializers.PrimaryKeyRelatedField(read_only=True)
    patient_data = serializers.SerializerMethodField()

    def get_patient_data(self, obj):
        if obj.patient:
            return {
                'id': obj.patient.id,
                'full_name': obj.patient.full_name,
                'mrn': obj.patient.mrn,
                'phone': obj.patient.phone,
                'age': obj.patient.age,
                'gender': obj.patient.gender,
            }
        return None

    class Meta:
        model = Transaction
        fields = [
            'id',
            'image_url',
            'diagnosis',
            'confidence',
            'model_version',
            'processing_time',
            # patient linkage
            'patient',
            'patient_data',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at', 'patient']


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'created_by', 'full_name', 'mrn', 'phone', 'age', 'gender', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class UploadImageSerializer(serializers.Serializer):
    """
    Serializer for image upload requests.
    """
    image = serializers.ImageField(required=True)
    patient_id = serializers.IntegerField(required=False)
    # patient info
    patient_name = serializers.CharField(max_length=255, required=False)
    age = serializers.IntegerField(min_value=0, max_value=150, required=False)
    gender = serializers.ChoiceField(choices=['M', 'F', 'O'], required=False)
    mrn = serializers.CharField(max_length=100, required=False)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_image(self, value):
        """
        Validate uploaded image.
        """
        # Check file size (10MB max)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image file size must be less than 10MB.")
        
        # Check file format
        allowed_formats = ['image/jpeg', 'image/jpg', 'image/png']
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError("Only JPG and PNG images are allowed.")
        
        return value

    def validate(self, attrs):
        """Allow either patient_id or full patient fields for backward compatibility."""
        patient_id = attrs.get('patient_id')
        legacy_fields = ['patient_name', 'age', 'gender', 'mrn']
        if not patient_id:
            missing = [f for f in legacy_fields if not attrs.get(f)]
            if missing:
                raise serializers.ValidationError(
                    {
                        'patient': 'Provide either patient_id or complete patient fields (patient_name, age, gender, mrn).',
                        'missing_fields': missing,
                    }
                )
        else:
            # If patient_id provided, ensure it exists
            if not Patient.objects.filter(id=patient_id).exists():
                raise serializers.ValidationError({'patient_id': 'Patient not found.'})
        return attrs


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    avatar = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'full_name', 'contact', 'avatar', 'role', 'created_at', 'updated_at']
        read_only_fields = ['username', 'created_at', 'updated_at']
    
    def update(self, instance, validated_data):
        # Update user email if provided
        user_data = validated_data.pop('user', {})
        if 'email' in user_data:
            instance.user.email = user_data['email']
            instance.user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for chat."""
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    avatar = serializers.ImageField(source='profile.avatar', read_only=True)
    role = serializers.CharField(source='profile.role', read_only=True)
    online = serializers.SerializerMethodField()

    def get_online(self, obj):
        try:
            from django.core.cache import cache
            return bool(cache.get(f'user_online_{obj.id}', False))
        except Exception:
            return False
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'avatar', 'role', 'online']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    sender = UserBasicSerializer(read_only=True)
    is_read = serializers.SerializerMethodField()
    
    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.read_by.filter(id=request.user.id).exists()
        return False
    
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'attachment_url', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for chat rooms."""
    members = UserBasicSerializer(many=True, read_only=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'content': last_msg.content,
                'sender': last_msg.sender.username,
                'created_at': last_msg.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.messages.exclude(read_by=request.user).exclude(sender=request.user).count()
        return 0
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'members', 'member_ids', 
            'patient', 'created_by', 'last_message', 'unread_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        request = self.context.get('request')
        
        # Create room
        room = ChatRoom.objects.create(
            created_by=request.user if request else None,
            **validated_data
        )
        
        # Normalize member IDs to integers
        normalized_ids = []
        for mid in member_ids:
            try:
                normalized_ids.append(int(mid))
            except (ValueError, TypeError):
                pass
        
        # Add current user to member list
        if request and request.user:
            normalized_ids.append(request.user.id)
        
        # Remove duplicates and add all members at once
        unique_ids = list(set(normalized_ids))
        if unique_ids:
            room.members.set(User.objects.filter(id__in=unique_ids))
        
        return room


# ==================== Treatment Management Serializers ====================

class TreatmentPlanSerializer(serializers.ModelSerializer):
    """Serializer for TreatmentPlan model."""
    created_by_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            profile = getattr(obj.created_by, 'profile', None)
            return profile.full_name if profile and profile.full_name else obj.created_by.username
        return None
    
    def get_patient_name(self, obj):
        return obj.patient.full_name if obj.patient else None
    
    class Meta:
        model = TreatmentPlan
        fields = [
            'id', 'patient', 'patient_name', 'diagnosis', 'title', 'description',
            'start_date', 'end_date', 'status', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient', 'patient_name', 'created_by', 'created_by_name', 'created_at', 'updated_at']


class MedicationSerializer(serializers.ModelSerializer):
    """Serializer for Medication model."""
    prescribed_by_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    
    def get_prescribed_by_name(self, obj):
        if obj.prescribed_by:
            profile = getattr(obj.prescribed_by, 'profile', None)
            return profile.full_name if profile and profile.full_name else obj.prescribed_by.username
        return None
    
    def get_patient_name(self, obj):
        return obj.patient.full_name if obj.patient else None
    
    class Meta:
        model = Medication
        fields = [
            'id', 'patient', 'patient_name', 'treatment_plan', 'drug_name', 'dosage',
            'frequency', 'route', 'instructions', 'start_date', 'end_date', 'status',
            'prescribed_by', 'prescribed_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient', 'patient_name', 'prescribed_by', 'prescribed_by_name', 'created_at', 'updated_at']


class FollowUpNoteSerializer(serializers.ModelSerializer):
    """Serializer for FollowUpNote model."""
    created_by_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            profile = getattr(obj.created_by, 'profile', None)
            return profile.full_name if profile and profile.full_name else obj.created_by.username
        return None
    
    def get_patient_name(self, obj):
        return obj.patient.full_name if obj.patient else None
    
    class Meta:
        model = FollowUpNote
        fields = [
            'id', 'patient', 'patient_name', 'treatment_plan', 'title', 'note',
            'note_type', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient', 'patient_name', 'created_by', 'created_by_name', 'created_at', 'updated_at']
