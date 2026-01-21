from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('home/', views.dashboard, name='dashboard'),

    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/create/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_edit, name='patient_edit'),
    path('patients/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
    path('patients/<int:pk>/screening/', views.health_screening_create, name='health_screening_create'),

    # Appointments
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/edit/', views.appointment_edit, name='appointment_edit'),
    path('appointments/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
    path('appointments/<int:pk>/complete/', views.appointment_complete, name='appointment_complete'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('appointments/<int:pk>/noshow/', views.appointment_noshow, name='appointment_noshow'),

    # Voice transcription
    path('transcribe-audio/', views.transcribe_audio, name='transcribe_audio'),

    # Protocols
    path('patients/<int:pk>/protocols/', views.protocol_list, name='protocol_list'),
    path('patients/<int:pk>/protocols/create/', views.protocol_create, name='protocol_create'),
    path('protocols/<int:pk>/', views.protocol_detail, name='protocol_detail'),

    # API endpoints for GPT extraction
    path('api/extract-from-transcript/', views.extract_from_transcript, name='extract_from_transcript'),
    path('api/protocol-schema/', views.get_protocol_schema, name='get_protocol_schema'),
]
