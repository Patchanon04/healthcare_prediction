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
    # patient-centric endpoints
    path('patients/', views.PatientListCreateView.as_view(), name='patients'),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient-detail'),
    path('patients/<int:patient_id>/transactions/', views.PatientTransactionsView.as_view(), name='patient-transactions'),
    path('health/', views.health_check, name='health'),
    path('seed-accounts/', views.seed_accounts, name='seed-accounts'),
    # auth
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/me/', views.me, name='me'),
    path('auth/profile/', views.profile, name='profile'),
]
