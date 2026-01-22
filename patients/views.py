from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta
from .models import Staff
from .models import Patient, Appointment, HealthScreening
import sys
import os

# Add parent directory to path to import ml_models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_models.predictor import (
    predict_noshow,
    predict_diabetes,
    predict_heart_disease,
    get_risk_level_uzbek
)


def dashboard(request):
    """Dashboard with statistics and today's appointments"""
    today = timezone.now().date()

    # Statistics
    total_patients = Patient.objects.count()
    today_appointments = Appointment.objects.filter(
        uchrashuv_sanasi__date=today
    ).count()

    high_risk_count = Appointment.objects.filter(
        uchrashuv_sanasi__date=today,
        kelmay_qolish_riski__gte=0.7
    ).count()

    completed_today = Appointment.objects.filter(
        uchrashuv_sanasi__date=today,
        holat='yakunlangan'
    ).count()

    # Today's appointments
    todays_appointments = Appointment.objects.filter(
        uchrashuv_sanasi__date=today
    ).select_related('bemor').order_by('uchrashuv_sanasi')[:10]

    # High-risk patients
    high_risk_appointments = Appointment.objects.filter(
        holat='rejalashtirilgan',
        kelmay_qolish_riski__gte=0.7
    ).select_related('bemor').order_by('-kelmay_qolish_riski')[:5]

    # Department statistics
    dept_stats = Appointment.objects.filter(
        uchrashuv_sanasi__date=today
    ).values('bolim').annotate(count=Count('id'))

    context = {
        'total_patients': total_patients,
        'today_appointments': today_appointments,
        'high_risk_count': high_risk_count,
        'completed_today': completed_today,
        'todays_appointments': todays_appointments,
        'high_risk_appointments': high_risk_appointments,
        'dept_stats': dept_stats,
    }

    return render(request, 'dashboard.html', context)

def staff_list(request):
    """List of staff members"""
    query = request.GET.get('q', '')

    if query:
        staff = Staff.objects.filter(
            Q(ism__icontains=query) |
            Q(lavozim__icontains=query) |
            Q(bolim__icontains=query)
        )
    else:
        staff = Staff.objects.all()

    context = {
        'staff': staff,
        'query': query,
    }
    return render(request, 'staff/staff_list.html', context)

def patient_list(request):
    """List all patients with search"""
    query = request.GET.get('q', '')

    if query:
        patients = Patient.objects.filter(
            Q(ism__icontains=query) | Q(telefon__icontains=query)
        )
    else:
        patients = Patient.objects.all()

    context = {
        'patients': patients,
        'query': query,
    }

    return render(request, 'patients/patient_list.html', context)


def patient_detail(request, pk):
    """Patient detail with AI health analysis"""
    patient = get_object_or_404(Patient, pk=pk)

    # Calculate AI predictions
    diabetes_risk = predict_diabetes(patient)
    heart_risk = predict_heart_disease(patient)

    # Get risk levels
    diabetes_risk_level = get_risk_level_uzbek(diabetes_risk)
    heart_risk_level = get_risk_level_uzbek(heart_risk)

    # Get appointments
    appointments = patient.uchrashuvlar.all()[:10]

    # Get health screenings
    screenings = patient.tekshiruvlar.all()[:5]

    context = {
        'patient': patient,
        'diabetes_risk': diabetes_risk,
        'heart_risk': heart_risk,
        'diabetes_risk_level': diabetes_risk_level,
        'heart_risk_level': heart_risk_level,
        'appointments': appointments,
        'screenings': screenings,
    }

    return render(request, 'patients/patient_detail.html', context)


def patient_create(request):
    """Create new patient"""
    if request.method == 'POST':
        try:
            patient = Patient.objects.create(
                ism=request.POST.get('ism'),
                yosh=int(request.POST.get('yosh')),
                jins=request.POST.get('jins'),
                telefon=request.POST.get('telefon'),
                manzil=request.POST.get('manzil', ''),
                qon_guruhi=request.POST.get('qon_guruhi', ''),
                allergiyalar=request.POST.get('allergiyalar', ''),
                qand_kasalligi=request.POST.get('qand_kasalligi') == 'on',
                gipertoniya=request.POST.get('gipertoniya') == 'on',
                yurak_kasalligi=request.POST.get('yurak_kasalligi') == 'on',
            )
            messages.success(request, f"Bemor {patient.ism} muvaffaqiyatli qo'shildi!")
            return redirect('patient_detail', pk=patient.pk)
        except Exception as e:
            messages.error(request, f"Xato: {str(e)}")

    return render(request, 'patients/patient_form.html')


def patient_edit(request, pk):
    """Edit patient"""
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        try:
            patient.ism = request.POST.get('ism')
            patient.yosh = int(request.POST.get('yosh'))
            patient.jins = request.POST.get('jins')
            patient.telefon = request.POST.get('telefon')
            patient.manzil = request.POST.get('manzil', '')
            patient.qon_guruhi = request.POST.get('qon_guruhi', '')
            patient.allergiyalar = request.POST.get('allergiyalar', '')
            patient.qand_kasalligi = request.POST.get('qand_kasalligi') == 'on'
            patient.gipertoniya = request.POST.get('gipertoniya') == 'on'
            patient.yurak_kasalligi = request.POST.get('yurak_kasalligi') == 'on'
            patient.save()

            messages.success(request, "Bemor ma'lumotlari yangilandi!")
            return redirect('patient_detail', pk=patient.pk)
        except Exception as e:
            messages.error(request, f"Xato: {str(e)}")

    context = {'patient': patient, 'is_edit': True}
    return render(request, 'patients/patient_form.html', context)


def patient_delete(request, pk):
    """Delete patient"""
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        patient.delete()
        messages.success(request, "Bemor o'chirildi!")
        return redirect('patient_list')

    return redirect('patient_detail', pk=pk)


def appointment_list(request):
    """List all appointments with filters"""
    appointments = Appointment.objects.select_related('bemor').all()

    # Apply filters
    holat = request.GET.get('holat', '')
    risk = request.GET.get('risk', '')
    date_filter = request.GET.get('date', '')

    if holat:
        appointments = appointments.filter(holat=holat)

    if risk == 'past':
        appointments = appointments.filter(kelmay_qolish_riski__lt=0.3)
    elif risk == 'orta':
        appointments = appointments.filter(kelmay_qolish_riski__gte=0.3, kelmay_qolish_riski__lt=0.7)
    elif risk == 'yuqori':
        appointments = appointments.filter(kelmay_qolish_riski__gte=0.7)

    today = timezone.now().date()
    if date_filter == 'bugun':
        appointments = appointments.filter(uchrashuv_sanasi__date=today)
    elif date_filter == 'ertaga':
        appointments = appointments.filter(uchrashuv_sanasi__date=today + timedelta(days=1))
    elif date_filter == 'hafta':
        appointments = appointments.filter(
            uchrashuv_sanasi__date__range=[today, today + timedelta(days=7)]
        )

    context = {
        'appointments': appointments[:50],
        'holat': holat,
        'risk': risk,
        'date_filter': date_filter,
    }

    return render(request, 'appointments/appointment_list.html', context)


def appointment_create(request):
    """Create new appointment with AI risk prediction"""
    if request.method == 'POST':
        try:
            patient_id = request.POST.get('bemor')
            patient = Patient.objects.get(pk=patient_id)

            # Create appointment
            appointment = Appointment(
                bemor=patient,
                uchrashuv_sanasi=request.POST.get('uchrashuv_sanasi'),
                shifokor=request.POST.get('shifokor'),
                bolim=request.POST.get('bolim'),
                sms_yuborildi=request.POST.get('sms_yuborildi') == 'on',
                izoh=request.POST.get('izoh', ''),
            )
            appointment.save()

            # Calculate AI predictions
            noshow_risk = predict_noshow(patient, appointment)
            diabetes_risk = predict_diabetes(patient)
            heart_risk = predict_heart_disease(patient)

            appointment.kelmay_qolish_riski = noshow_risk
            appointment.qand_riski = diabetes_risk
            appointment.yurak_riski = heart_risk
            appointment.save()

            # Update patient stats
            patient.umumiy_uchrashuvlar += 1
            patient.save()

            # Show warning if high risk
            if noshow_risk >= 0.7:
                messages.warning(
                    request,
                    f"Diqqat! Kelmay qolish riski yuqori: {noshow_risk*100:.1f}%"
                )
            else:
                messages.success(request, "Uchrashuv muvaffaqiyatli yaratildi!")

            return redirect('appointment_list')
        except Exception as e:
            messages.error(request, f"Xato: {str(e)}")

    # Get all patients for dropdown
    patients = Patient.objects.all().order_by('ism')

    context = {'patients': patients}
    return render(request, 'appointments/appointment_form.html', context)


def appointment_edit(request, pk):
    """Edit appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == 'POST':
        try:
            appointment.uchrashuv_sanasi = request.POST.get('uchrashuv_sanasi')
            appointment.shifokor = request.POST.get('shifokor')
            appointment.bolim = request.POST.get('bolim')
            appointment.sms_yuborildi = request.POST.get('sms_yuborildi') == 'on'
            appointment.izoh = request.POST.get('izoh', '')
            appointment.save()

            messages.success(request, "Uchrashuv yangilandi!")
            return redirect('appointment_list')
        except Exception as e:
            messages.error(request, f"Xato: {str(e)}")

    patients = Patient.objects.all().order_by('ism')
    context = {'appointment': appointment, 'patients': patients, 'is_edit': True}
    return render(request, 'appointments/appointment_form.html', context)


def appointment_delete(request, pk):
    """Delete appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Uchrashuv o'chirildi!")
        return redirect('appointment_list')

    return redirect('appointment_list')


def appointment_complete(request, pk):
    """Mark appointment as completed"""
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.holat = 'yakunlangan'
    appointment.save()
    messages.success(request, "Uchrashuv yakunlandi!")
    return redirect('appointment_list')


def appointment_cancel(request, pk):
    """Cancel appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.holat = 'bekor_qilingan'
    appointment.save()
    messages.warning(request, "Uchrashuv bekor qilindi!")
    return redirect('appointment_list')


def appointment_noshow(request, pk):
    """Mark appointment as no-show"""
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.holat = 'kelmagan'
    appointment.save()

    # Update patient no-show count
    patient = appointment.bemor
    patient.kelmaganlar_soni += 1
    patient.save()

    messages.info(request, "Uchrashuv 'kelmagan' deb belgilandi!")
    return redirect('appointment_list')


def health_screening_create(request, pk):
    """Create health screening with AI analysis"""
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        try:
            # Get form data
            qon_bosimi_yuqori = request.POST.get('qon_bosimi_yuqori')
            qon_bosimi_past = request.POST.get('qon_bosimi_past')
            glyukoza = request.POST.get('glyukoza')
            bmi = request.POST.get('bmi')

            # Create screening
            screening = HealthScreening(
                bemor=patient,
                qon_bosimi_yuqori=int(qon_bosimi_yuqori) if qon_bosimi_yuqori else None,
                qon_bosimi_past=int(qon_bosimi_past) if qon_bosimi_past else None,
                puls=int(request.POST.get('puls')) if request.POST.get('puls') else None,
                harorat=float(request.POST.get('harorat')) if request.POST.get('harorat') else None,
                glyukoza=float(glyukoza) if glyukoza else None,
                holesterin=float(request.POST.get('holesterin')) if request.POST.get('holesterin') else None,
                bmi=float(bmi) if bmi else None,
                izoh=request.POST.get('izoh', ''),
            )

            # Calculate AI predictions
            diabetes_risk = predict_diabetes(
                patient,
                glucose=float(glyukoza) if glyukoza else None,
                bmi=float(bmi) if bmi else None,
                blood_pressure=int(qon_bosimi_past) if qon_bosimi_past else None
            )

            heart_risk = predict_heart_disease(
                patient,
                blood_pressure=int(qon_bosimi_yuqori) if qon_bosimi_yuqori else None,
                cholesterol=float(request.POST.get('holesterin')) if request.POST.get('holesterin') else None
            )

            screening.qand_ehtimoli = diabetes_risk
            screening.yurak_ehtimoli = heart_risk
            screening.save()

            messages.success(request, "Tekshiruv muvaffaqiyatli saqlandi!")
            return redirect('patient_detail', pk=patient.pk)
        except Exception as e:
            messages.error(request, f"Xato: {str(e)}")

    context = {'patient': patient}
    return render(request, 'patients/screening_form.html', context)

def staff_create(request):
    """Create new staff member"""
    if request.method == 'POST':
        try:
            staff = Staff.objects.create(
                ism=request.POST.get('ism'),
                lavozim=request.POST.get('lavozim'),
                bolim=request.POST.get('bolim'),
                telefon=request.POST.get('telefon'),
                email=request.POST.get('email', ''),
                faol=request.POST.get('faol') == 'on',
                ishga_olingan_sana=request.POST.get('ishga_olingan_sana'),
            )
            messages.success(request, f"Xodim {staff.ism} muvaffaqiyatli qo'shildi!")
            return redirect('staff_list')
        except Exception as e:
            messages.error(request, f"Xato: {str(e)}")

    context = {
        'lavozim_choices': Staff.LAVOZIM_CHOICES,
        'bolim_choices': Appointment.BOLIM_CHOICES,
    }
    return render(request, 'staff/staff_form.html', context)


def staff_edit(request, pk):
    """Edit staff member"""
    staff = get_object_or_404(Staff, pk=pk)

    if request.method == 'POST':
        try:
            staff.ism = request.POST.get('ism')
            staff.lavozim = request.POST.get('lavozim')
            staff.bolim = request.POST.get('bolim')
            staff.telefon = request.POST.get('telefon')
            staff.email = request.POST.get('email', '')
            staff.faol = request.POST.get('faol') == 'on'
            staff.ishga_olingan_sana = request.POST.get('ishga_olingan_sana')
            staff.save()

            messages.success(request, "Xodim ma'lumotlari yangilandi!")
            return redirect('staff_list')
        except Exception as e:
            messages.error(request, f"Xato: {str(e)}")

    context = {
        'staff': staff,
        'is_edit': True,
        'lavozim_choices': Staff.LAVOZIM_CHOICES,
        'bolim_choices': Appointment.BOLIM_CHOICES,
    }
    return render(request, 'staff/staff_form.html', context)


def staff_delete(request, pk):
    """Delete staff member"""
    staff = get_object_or_404(Staff, pk=pk)

    if request.method == 'POST':
        staff.delete()
        messages.success(request, f"Xodim {staff.ism} o'chirildi!")
        return redirect('staff_list')

    return redirect('staff_list')