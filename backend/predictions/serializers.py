"""
Serializers for medical diagnosis predictions API.
"""
from rest_framework import serializers
from .models import Transaction, UserProfile, Patient
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
        fields = ['id', 'full_name', 'mrn', 'phone', 'age', 'gender', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


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


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user


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
