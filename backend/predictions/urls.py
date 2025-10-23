"""
URL patterns for predictions API v1.
"""
from django.urls import path
from . import views

app_name = 'predictions'

urlpatterns = [
    path('upload/', views.upload_image, name='upload'),
    path('history/', views.TransactionHistoryView.as_view(), name='history'),
    path('history/<uuid:pk>/', views.TransactionDetailView.as_view(), name='history-detail'),
    path('health/', views.health_check, name='health'),
    # auth
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/me/', views.me, name='me'),
]
