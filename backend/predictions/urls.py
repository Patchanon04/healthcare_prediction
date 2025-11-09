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
    # appointments
    path('appointments/', views.AppointmentListCreateView.as_view(), name='appointments'),
    path('appointments/<int:pk>/', views.AppointmentDetailView.as_view(), name='appointment-detail'),
    # second opinion workflow
    path('second-opinions/', views.SecondOpinionRequestListCreateView.as_view(), name='second-opinion-list'),
    path('second-opinions/<uuid:pk>/', views.SecondOpinionRequestDetailView.as_view(), name='second-opinion-detail'),
    # auth (register removed)
    path('auth/login/', views.login, name='login'),
    path('auth/me/', views.me, name='me'),
    path('auth/profile/', views.profile, name='profile'),
    # metrics (dashboard)
    path('metrics/summary/', views.metrics_summary, name='metrics-summary'),
    path('metrics/daily/', views.metrics_daily, name='metrics-daily'),
    path('metrics/diagnosis-distribution/', views.metrics_diagnosis_distribution, name='metrics-diagnosis'),
    # reports
    path('reports/summary/', views.reports_summary, name='reports-summary'),
    # chat
    path('chat/users/', views.list_users, name='chat-users'),
    path('chat/rooms/', views.ChatRoomListCreateView.as_view(), name='chat-rooms'),
    path('chat/rooms/<uuid:pk>/', views.ChatRoomDetailView.as_view(), name='chat-room-detail'),
    path('chat/rooms/<uuid:room_id>/messages/', views.MessageListCreateView.as_view(), name='chat-messages'),
    path('chat/rooms/<uuid:room_id>/read/', views.mark_messages_read, name='mark-read'),
    path('chat/unread-count/', views.get_unread_count, name='unread-count'),
    # global search
    path('search/', views.global_search, name='global-search'),
    # treatment management
    path('patients/<int:patient_id>/treatments/', views.TreatmentPlanListCreateView.as_view(), name='patient-treatments'),
    path('patients/<int:patient_id>/treatments/<uuid:pk>/', views.TreatmentPlanDetailView.as_view(), name='patient-treatment-detail'),
    path('patients/<int:patient_id>/medications/', views.MedicationListCreateView.as_view(), name='patient-medications'),
    path('patients/<int:patient_id>/medications/<uuid:pk>/', views.MedicationDetailView.as_view(), name='patient-medication-detail'),
    path('patients/<int:patient_id>/followups/', views.FollowUpNoteListCreateView.as_view(), name='patient-followups'),
    path('patients/<int:patient_id>/followups/<uuid:pk>/', views.FollowUpNoteDetailView.as_view(), name='patient-followup-detail'),
    path('patients/<int:patient_id>/timeline/', views.patient_timeline, name='patient-timeline'),
]
