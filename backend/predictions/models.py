"""
Database models for dog breed predictions.
"""
import uuid
from django.db import models


class Transaction(models.Model):
    """
    Model to store dog breed prediction transactions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['uploaded_at'], name='uploaded_at_idx'),
        ]

    def __str__(self):
        return f"{self.diagnosis} - {self.confidence:.2f} ({self.uploaded_at})"
