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
    list_display = ['id', 'breed', 'confidence', 'model_version', 'uploaded_at']
    list_filter = ['breed', 'model_version', 'uploaded_at']
    search_fields = ['id', 'breed', 'image_url']
    readonly_fields = ['id', 'uploaded_at']
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('Image Information', {
            'fields': ('id', 'image_url')
        }),
        ('Prediction Results', {
            'fields': ('breed', 'confidence', 'model_version', 'processing_time')
        }),
        ('Metadata', {
            'fields': ('uploaded_at',)
        }),
    )
