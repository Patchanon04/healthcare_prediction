"""
Serializers for dog breed predictions API.
"""
from rest_framework import serializers
from .models import Transaction
from django.contrib.auth.models import User


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    """
    class Meta:
        model = Transaction
        fields = [
            'id',
            'image_url',
            'diagnosis',
            'confidence',
            'model_version',
            'processing_time',
            # patient info
            'patient_name',
            'age',
            'gender',
            'mrn',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']


class UploadImageSerializer(serializers.Serializer):
    """
    Serializer for image upload requests.
    """
    image = serializers.ImageField(required=True)
    # patient info
    patient_name = serializers.CharField(max_length=255)
    age = serializers.IntegerField(min_value=0, max_value=150)
    gender = serializers.ChoiceField(choices=['M', 'F', 'O'])
    mrn = serializers.CharField(max_length=100)

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
