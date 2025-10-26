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


class ChatRoom(models.Model):
    """
    Chat room for real-time messaging between users.
    Can be direct message (2 users) or group chat.
    """
    ROOM_TYPE_CHOICES = [
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
        ('case', 'Case Discussion'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, help_text="Room name for group chats")
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='direct')
    members = models.ManyToManyField(User, related_name='chat_rooms')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='chat_rooms', null=True, blank=True, help_text="Associated patient for case discussions")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['room_type'], name='room_type_idx'),
            models.Index(fields=['updated_at'], name='room_updated_idx'),
        ]
    
    def __str__(self):
        if self.name:
            return self.name
        members = self.members.all()[:2]
        return f"Chat: {', '.join([u.username for u in members])}"


class Message(models.Model):
    """
    Individual message in a chat room.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    attachment_url = models.URLField(max_length=500, blank=True, help_text="URL to attached file/image")
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at'], name='room_created_idx'),
        ]
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


# ==================== Treatment Management Models ====================

class TreatmentPlan(models.Model):
    """
    Treatment plan for a patient.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatment_plans')
    diagnosis = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name='treatment_plans', help_text="Related diagnosis/transaction")
    title = models.CharField(max_length=200, help_text="Treatment plan title")
    description = models.TextField(help_text="Detailed treatment plan")
    start_date = models.DateField(help_text="Treatment start date")
    end_date = models.DateField(null=True, blank=True, help_text="Expected end date")
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='active'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_treatment_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'treatment_plans'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at'], name='patient_treatment_idx'),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.title}"


class Medication(models.Model):
    """
    Medication history for a patient.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medications')
    treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='medications')
    drug_name = models.CharField(max_length=200, help_text="Medication name")
    dosage = models.CharField(max_length=100, help_text="Dosage (e.g., 500mg)")
    frequency = models.CharField(max_length=100, help_text="Frequency (e.g., twice daily)")
    route = models.CharField(max_length=50, blank=True, help_text="Route of administration (e.g., oral, IV)")
    instructions = models.TextField(blank=True, help_text="Special instructions")
    start_date = models.DateField(help_text="Start date")
    end_date = models.DateField(null=True, blank=True, help_text="End date")
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('discontinued', 'Discontinued'),
        ],
        default='active'
    )
    prescribed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prescribed_medications')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'medications'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['patient', '-start_date'], name='patient_medication_idx'),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.drug_name}"


class FollowUpNote(models.Model):
    """
    Follow-up notes for tracking patient progress.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='followup_notes')
    treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='followup_notes')
    title = models.CharField(max_length=200, help_text="Note title")
    note = models.TextField(help_text="Follow-up note content")
    note_type = models.CharField(
        max_length=20,
        choices=[
            ('checkup', 'Check-up'),
            ('progress', 'Progress Update'),
            ('complication', 'Complication'),
            ('other', 'Other'),
        ],
        default='progress'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_followup_notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'followup_notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at'], name='patient_followup_idx'),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.title}"
