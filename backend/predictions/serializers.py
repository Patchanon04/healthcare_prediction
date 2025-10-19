"""
Serializers for dog breed predictions API.
"""
from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    """
    class Meta:
        model = Transaction
        fields = [
            'id',
            'image_url',
            'breed',
            'confidence',
            'model_version',
            'processing_time',
            'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']


class UploadImageSerializer(serializers.Serializer):
    """
    Serializer for image upload requests.
    """
    image = serializers.ImageField(required=True)

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
