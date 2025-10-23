"""
Admin configuration for predictions app.
"""
from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Admin interface for Transaction model.
    """
    list_display = ['id', 'diagnosis', 'confidence', 'model_version', 'patient_name', 'age', 'gender', 'mrn', 'uploaded_at']
    list_filter = ['diagnosis', 'model_version', 'gender', 'uploaded_at']
    search_fields = ['id', 'diagnosis', 'image_url', 'patient_name', 'mrn']
    readonly_fields = ['id', 'uploaded_at']
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('id', 'image_url')
        }),
        ('Prediction Results', {
            'fields': ('diagnosis', 'confidence', 'model_version', 'processing_time')
        }),
        ('Patient Information', {
            'fields': ('patient_name', 'age', 'gender', 'mrn')
        }),
        ('Metadata', {
            'fields': ('uploaded_at',)
        }),
    )
