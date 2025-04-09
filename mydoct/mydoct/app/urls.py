from django.urls import path
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/login/'), name='root_redirect'),
    path('login/', views.doctor_login, name='login'),
    path('logout/', views.doctor_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('appointments/', views.manage_appointments, name='manage_appointments'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('appointments/add/<int:patient_id>/', views.add_appointment, name='add_appointment_for_patient'),
    path('appointments/view/<int:appointment_id>/', views.view_appointment, name='view_appointment'),
    path('appointments/edit/<int:appointment_id>/', views.edit_appointment, name='edit_appointment'),
    path('add-staff/', views.add_staff, name='add_staff'),
    path('patients/edit/<int:patient_id>/', views.edit_patient, name='edit_patient'),  # Added URL for edit_patient
    path('appointments/delete/<int:appointment_id>/', views.delete_appointment, name='delete_appointment'),
    path('appointments/<int:appointment_id>/update_status/', views.update_appointment_status, name='update_appointment_status'),
    path('patients/', views.list_patients, name='list_patients'),  # Added URL for list_patients
    path('patients/delete/<int:patient_id>/', views.delete_patient, name='delete_patient'),  # Added URL for delete_patient

]
