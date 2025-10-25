"""
Database models for medical diagnosis predictions.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extended user profile with additional medical professional information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=50, blank=True, help_text="Phone number or contact info")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Profile picture")
    role = models.CharField(
        max_length=50,
        choices=[
            ('doctor', 'Doctor'),
            ('nurse', 'Nurse'),
            ('radiologist', 'Radiologist'),
            ('admin', 'Admin'),
        ],
        default='doctor'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Patient(models.Model):
    """
    Patient master record to store PII and clinical identifiers.
    """
    # Using auto-increment integer ID for simplicity
    full_name = models.CharField(max_length=255)
    mrn = models.CharField(max_length=100, help_text="Medical Record Number", db_index=True)
    phone = models.CharField(max_length=20, blank=True, default='', help_text="Patient phone number", db_index=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patients'
        indexes = [
            models.Index(fields=['mrn'], name='patient_mrn_idx'),
            models.Index(fields=['full_name'], name='patient_name_idx'),
            models.Index(fields=['phone'], name='patient_phone_idx'),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.mrn})"


class Transaction(models.Model):
    """
    Model to store medical diagnosis prediction transactions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    patient = models.ForeignKey('Patient', on_delete=models.SET_NULL, related_name='transactions', null=True, blank=True)
    image_url = models.URLField(max_length=500)
    diagnosis = models.CharField(max_length=100)
    confidence = models.FloatField()
    model_version = models.CharField(max_length=20)
    processing_time = models.FloatField(help_text="Processing time in seconds")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['uploaded_at'], name='uploaded_at_idx'),
            models.Index(fields=['patient'], name='transaction_patient_idx'),
        ]

    def __str__(self):
        return f"{self.diagnosis} - {self.confidence:.2f} ({self.uploaded_at})"
