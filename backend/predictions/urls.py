"""
URL patterns for predictions API v1.
"""
from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    path('upload/', views.upload_image, name='upload'),
    path('history/', views.TransactionHistoryView.as_view(), name='history'),
    path('health/', views.health_check, name='health'),
]
