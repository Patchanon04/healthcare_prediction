"""
Database models for medical diagnosis predictions.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extended user profile for medical professionals.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=50, blank=True)
    role = models.CharField(
        max_length=20,
        choices=[
            ('doctor', 'Doctor'),
            ('nurse', 'Nurse'),
            ('specialist', 'Specialist'),
            ('researcher', 'Researcher'),
        ],
        default='doctor'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Transaction(models.Model):
    """
    Model to store medical diagnosis prediction transactions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    image_url = models.URLField(max_length=500)
    diagnosis = models.CharField(max_length=100)
    confidence = models.FloatField()
    model_version = models.CharField(max_length=20)
    processing_time = models.FloatField(help_text="Processing time in seconds")
    # Patient information
    patient_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    mrn = models.CharField(max_length=100, help_text="Medical Record Number")
    phone = models.CharField(max_length=20, blank=True, help_text="Patient phone number")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['uploaded_at'], name='uploaded_at_idx'),
        ]

    def __str__(self):
        return f"{self.diagnosis} - {self.confidence:.2f} ({self.uploaded_at})"
