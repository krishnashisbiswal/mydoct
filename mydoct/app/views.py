from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Doctor, Patient, Appointment
from .forms import PatientForm, AppointmentForm
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.contrib.auth.hashers import make_password
import json
from django.http import JsonResponse

@csrf_protect
def doctor_login(request):
    if request.method == 'POST':
        try:
            username = request.POST['username']
            password = request.POST['password']
            role = request.POST['role']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if (role == 'admin' and user.is_superuser) or \
                   (role == 'doctor' and user.is_staff and user.specialization) or \
                   (role == 'staff' and user.is_staff and not user.specialization):
                    login(request, user)
                    return redirect('dashboard')
                else:
                    return render(request, 'login.html', {'error': f'Invalid role selection. Please login as {"admin" if user.is_superuser else "doctor" if user.specialization else "staff"}'})
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})
        except Exception as e:
            return render(request, 'login.html', {'error': 'An error occurred. Please try again.'})
    return render(request, 'login.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_staff(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        specialization = request.POST.get('specialization', '')
        if Doctor.objects.filter(email=email).exists():
            return render(request, 'add_staff.html', {'error': 'Email already exists. Please use a different email address.'})
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while Doctor.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        try:
            is_doctor = role == 'doctor'
            doctor = Doctor.objects.create(
                username=username,
                name=name,
                email=email,
                password=make_password(password),
                is_staff=True,
                is_active=True,
                specialization=specialization,
               
            )
            return redirect('list_staff')
        except Exception as e:
            return render(request, 'add_staff.html', {
                'error': f'Error creating staff: {str(e)}'
            })
    return render(request, 'add_staff.html')

@login_required
def doctor_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user = request.user
    if user.is_superuser:
        user.display_name = f"Admin {user.name}"
    elif user.specialization:
        user.display_name = f"Doctor {user.name}"
    else:
        user.display_name = f"Staff {user.name}"
    
    appointments = Appointment.objects.filter(doctor=user).order_by('-date', '-time')
    return render(request, 'dashboard.html', {'user': user,'appointments': appointments})

@login_required
def list_staff(request):
    staff_members = Doctor.objects.filter(is_staff=True).order_by('name')
    return render(request, 'list_staff.html', {'staff_members': staff_members})

@login_required
def list_patients(request):
    patients = Patient.objects.all().order_by('name')
    for patient in patients:
        print(f"Patient Name: {patient.name}, Phone Number: {patient.phone_number}")
    return render(request, 'list_patients.html', {'patients': patients})

@login_required
def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('list_patients')
    else:
        form = PatientForm(instance=patient)
    return render(request, 'edit_patient.html', {'form': form})

@login_required
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    patient.delete()
    return redirect('list_patients')

def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            return redirect('patient_detail', patient_id=patient.id)
    else:
        form = PatientForm()
    return render(request, 'add_patient.html', {'form': form})

@login_required
def view_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    return render(request, 'view_appointment.html', {'appointment': appointment})

@login_required
def edit_appointment(request, appointment_id):
    if request.user.is_superuser:
        appointment = get_object_or_404(Appointment, id=appointment_id)
    else:
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment.doctor = form.cleaned_data['doctor']
            form.save()
            return redirect('manage_appointments')
    else:
        form = AppointmentForm(instance=appointment)
    
    doctors = Doctor.objects.filter(is_staff=False, specialization__isnull=False)

    return render(request, 'edit_appointment.html', {
        'doctors': doctors,
        'form': form,
        'appointment': appointment
    })

@login_required
def manage_appointments(request):
    user = request.user
    appointments = Appointment.objects.all().order_by('-date', '-time')
    return render(request, 'manage_appointments.html', {
        'appointments': appointments,
        'user': user
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_appointment(request, patient_id=None):
    doctors = Doctor.objects.filter(specialization__isnull=False, is_staff=True)
    doctor = request.user
    patient = get_object_or_404(Patient, id=patient_id) if patient_id else None
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            if patient:
                appointment.patient = patient
            appointment.save()
            return redirect('manage_appointments')
    else:
        form = AppointmentForm(initial={'doctor': doctor})
        form.fields['doctor'].queryset = doctors
    
    return render(request, 'add_appointment.html', {
        'form': form,
        'patient': patient
    })

@login_required
def patient_detail(request, patient_id):
    doctor = request.user
    patient = get_object_or_404(Patient, id=patient_id)
    appointments = Appointment.objects.filter(doctor=doctor, patient=patient)
    return render(request, 'patient_detail.html', {
        'patient': patient,
        'appointments': appointments
    })

@csrf_exempt
@login_required
def update_appointment_status(request, appointment_id):
    if request.method == 'POST':
        try:
            appointment = get_object_or_404(Appointment, id=appointment_id)
            data = json.loads(request.body)
            new_status = data.get('status')
            
            if new_status in dict(Appointment.STATUS_CHOICES).keys():
                appointment.status = new_status
                appointment.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.delete()
    return redirect('manage_appointments')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_staff(request, staff_id):
    staff_member = get_object_or_404(Doctor, id=staff_id)
    if request.method == 'POST':
        staff_member.name = request.POST['name']
        staff_member.email = request.POST['email']
        staff_member.specialization = request.POST.get('specialization', '')
        # Update the role based on the selected specialization
        if request.POST['role'] == 'doctor':
            staff_member.specialization = 'Doctor'
        else:
            staff_member.specialization = ''
        
        staff_member.save()
        return redirect('list_staff')
    return render(request, 'edit_staff.html', {'staff_member': staff_member})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_staff(request, staff_id):
    staff_member = get_object_or_404(Doctor, id=staff_id)
    staff_member.delete()
    return redirect('list_staff')