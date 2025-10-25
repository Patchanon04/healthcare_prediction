"""
Admin configuration for predictions app.
"""
from django.contrib import admin
from .models import Transaction, Patient


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
