"""
Admin configuration for predictions app.
"""
from django.contrib import admin
from .models import Transaction, Patient, ChatRoom, Message, TreatmentPlan, Medication, FollowUpNote


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for Transaction model.
    """
    list_display = ['id', 'diagnosis', 'confidence', 'model_version', 'patient_display', 'uploaded_at']
    list_filter = ['diagnosis', 'model_version', 'uploaded_at']
    search_fields = ['id', 'diagnosis', 'image_url', 'patient__full_name', 'patient__mrn', 'patient__phone']
    readonly_fields = ['id', 'uploaded_at']
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('id', 'image_url')
        }),
        ('Prediction Results', {
            'fields': ('diagnosis', 'confidence', 'model_version', 'processing_time')
        }),
        ('Patient', {
            'fields': ('patient',)
        }),
        ('Metadata', {
            'fields': ('uploaded_at',)
        }),
    )

    def patient_display(self, obj):
        if obj.patient:
            return f"{obj.patient.full_name} ({obj.patient.mrn or '-'})"
        return '-'
    patient_display.short_description = 'Patient'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'mrn', 'phone', 'age', 'gender', 'created_at']
    search_fields = ['full_name', 'mrn', 'phone']
    list_filter = ['gender', 'created_at']


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'room_type', 'member_count', 'created_by', 'created_at']
    list_filter = ['room_type', 'created_at']
    search_fields = ['name', 'members__username']
    filter_horizontal = ['members']
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'sender', 'content_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'sender__username', 'room__name']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(TreatmentPlan)
class TreatmentPlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'title', 'status', 'start_date', 'end_date', 'created_by', 'created_at']
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['title', 'description', 'patient__full_name', 'patient__mrn']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'drug_name', 'dosage', 'frequency', 'status', 'start_date', 'end_date']
    list_filter = ['status', 'start_date']
    search_fields = ['drug_name', 'patient__full_name', 'patient__mrn']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(FollowUpNote)
class FollowUpNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'title', 'note_type', 'created_by', 'created_at']
    list_filter = ['note_type', 'created_at']
    search_fields = ['title', 'note', 'patient__full_name', 'patient__mrn']
    readonly_fields = ['id', 'created_at', 'updated_at']
