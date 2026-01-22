from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from datetime import timedelta
from .models import Patient, Appointment, HealthScreening, Protocol
from .gpt_service import extract_medical_data_from_transcript, get_schema_for_protocol, extract_patient_data_from_transcript
import json
import sys
import os
from io import BytesIO
from elevenlabs.client import ElevenLabs

# Add parent directory to path to import ml_models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ml_models.predictor import (
    predict_noshow,
    predict_diabetes,
    predict_heart_disease,
    predict_diabetes_from_protocol,
    predict_heart_disease_from_protocol,
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

    # Calculate AI predictions (convert to percentages for display)
    diabetes_risk = predict_diabetes(patient) * 100
    heart_risk = predict_heart_disease(patient) * 100

    # Get risk levels (convert back to decimal for risk level calculation)
    diabetes_risk_level = get_risk_level_uzbek(diabetes_risk / 100)
    heart_risk_level = get_risk_level_uzbek(heart_risk / 100)

    # Get appointments
    appointments = patient.uchrashuvlar.all()[:10]

    # Get health screenings
    screenings = patient.tekshiruvlar.all()[:5]

    # Get protocols
    protocols = patient.protokollar.all()[:5]

    context = {
        'patient': patient,
        'diabetes_risk': diabetes_risk,
        'heart_risk': heart_risk,
        'diabetes_risk_level': diabetes_risk_level,
        'heart_risk_level': heart_risk_level,
        'appointments': appointments,
        'screenings': screenings,
        'protocols': protocols,
    }

    return render(request, 'patients/patient_detail.html', context)


def patient_create(request):
    """Create new patient"""
    if request.method == 'POST':
        try:
            # Validate required fields
            ism = request.POST.get('ism', '').strip()
            yosh_str = request.POST.get('yosh', '').strip()
            jins = request.POST.get('jins', '').strip()
            telefon = request.POST.get('telefon', '').strip()

            # Check required fields
            if not ism:
                messages.error(request, "Ism kiritilishi shart!")
                return render(request, 'patients/patient_form.html')
            if not yosh_str:
                messages.error(request, "Yosh kiritilishi shart!")
                return render(request, 'patients/patient_form.html')
            if not jins:
                messages.error(request, "Jins tanlanishi shart!")
                return render(request, 'patients/patient_form.html')
            if not telefon:
                messages.error(request, "Telefon kiritilishi shart!")
                return render(request, 'patients/patient_form.html')

            patient = Patient.objects.create(
                ism=ism,
                yosh=int(yosh_str),
                jins=jins,
                telefon=telefon,
                manzil=request.POST.get('manzil', ''),
                qon_guruhi=request.POST.get('qon_guruhi', ''),
                allergiyalar=request.POST.get('allergiyalar', ''),
                qand_kasalligi=request.POST.get('qand_kasalligi') == 'on',
                gipertoniya=request.POST.get('gipertoniya') == 'on',
                yurak_kasalligi=request.POST.get('yurak_kasalligi') == 'on',
            )
            messages.success(request, f"Bemor {patient.ism} muvaffaqiyatli qo'shildi!")
            return redirect('patient_detail', pk=patient.pk)
        except ValueError as e:
            messages.error(request, "Yosh to'g'ri formatda kiritilishi kerak!")
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


@csrf_exempt
def transcribe_audio(request):
    """Transcribe audio using ElevenLabs Speech-to-Text API"""
    if request.method == 'POST' and request.FILES.get('audio'):
        try:
            # Get the audio file from request
            audio_file = request.FILES['audio']
            audio_data = BytesIO(audio_file.read())
            
            # Initialize ElevenLabs client
            elevenlabs = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
            
            # Transcribe the audio
            transcription = elevenlabs.speech_to_text.convert(
                file=audio_data,
                model_id="scribe_v2",
                tag_audio_events=True,
                language_code="uzb",  # Uzbek language
                diarize=True,  # Annotate who is speaking
            )
            
            # Return the transcription text
            return JsonResponse({
                'success': True,
                'transcription': str(transcription.text if hasattr(transcription, 'text') else transcription),
                'message': 'Audio muvaffaqiyatli transkripsiya qilindi!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': f'Xato: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Audio fayl topilmadi'
    }, status=400)


# ============ PROTOCOL VIEWS ============

def protocol_list(request, pk):
    """List all protocols for a patient"""
    patient = get_object_or_404(Patient, pk=pk)
    protocols = patient.protokollar.all()

    context = {
        'patient': patient,
        'protocols': protocols,
    }
    return render(request, 'protocols/protocol_list.html', context)


def protocol_create(request, pk):
    """Create new protocol with voice recording and GPT extraction"""
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        try:
            protocol_type = request.POST.get('protocol_type')
            if not protocol_type:
                messages.error(request, "Protokol turi tanlanishi shart!")
                return render(request, 'protocols/protocol_form.html', {'patient': patient})

            # Create protocol instance
            protocol = Protocol(
                bemor=patient,
                protocol_type=protocol_type,
                shifokor=request.POST.get('shifokor', ''),
                izoh=request.POST.get('izoh', ''),
                transcript=request.POST.get('transcript', ''),
            )

            # Common medical fields
            protocol.qon_guruhi = request.POST.get('qon_guruhi') or None
            protocol.allergiyalar = request.POST.get('allergiyalar', '')
            protocol.qand_kasalligi = request.POST.get('qand_kasalligi') == 'on'
            protocol.gipertoniya = request.POST.get('gipertoniya') == 'on'
            protocol.yurak_kasalligi = request.POST.get('yurak_kasalligi') == 'on'

            # Diabetes-specific fields
            if protocol_type == 'diabetes':
                protocol.pregnancies = int(request.POST.get('pregnancies')) if request.POST.get('pregnancies') else None
                protocol.glucose = float(request.POST.get('glucose')) if request.POST.get('glucose') else None
                protocol.blood_pressure = int(request.POST.get('blood_pressure')) if request.POST.get('blood_pressure') else None
                protocol.skin_thickness = int(request.POST.get('skin_thickness')) if request.POST.get('skin_thickness') else None
                protocol.insulin = float(request.POST.get('insulin')) if request.POST.get('insulin') else None
                protocol.bmi = float(request.POST.get('bmi')) if request.POST.get('bmi') else None
                protocol.diabetes_pedigree = float(request.POST.get('diabetes_pedigree')) if request.POST.get('diabetes_pedigree') else None

            # Heart disease-specific fields
            elif protocol_type == 'heart':
                protocol.sex = int(request.POST.get('sex')) if request.POST.get('sex') else None
                protocol.chest_pain_type = int(request.POST.get('chest_pain_type')) if request.POST.get('chest_pain_type') else None
                protocol.resting_bp = int(request.POST.get('resting_bp')) if request.POST.get('resting_bp') else None
                protocol.cholesterol = float(request.POST.get('cholesterol')) if request.POST.get('cholesterol') else None
                protocol.fasting_blood_sugar = request.POST.get('fasting_blood_sugar') == 'on'
                protocol.rest_ecg = int(request.POST.get('rest_ecg')) if request.POST.get('rest_ecg') else None
                protocol.max_heart_rate = int(request.POST.get('max_heart_rate')) if request.POST.get('max_heart_rate') else None
                protocol.exercise_angina = request.POST.get('exercise_angina') == 'on'
                protocol.oldpeak = float(request.POST.get('oldpeak')) if request.POST.get('oldpeak') else None
                protocol.slope = int(request.POST.get('slope')) if request.POST.get('slope') else None
                protocol.num_vessels = int(request.POST.get('num_vessels')) if request.POST.get('num_vessels') else None
                protocol.thal = int(request.POST.get('thal')) if request.POST.get('thal') else None

            # Save protocol first (needed for FK relation in prediction)
            protocol.save()

            # Calculate AI risk prediction using ALL protocol fields
            if protocol_type == 'diabetes':
                risk = predict_diabetes_from_protocol(protocol)
            else:  # heart
                risk = predict_heart_disease_from_protocol(protocol)

            # Update protocol with prediction results
            protocol.ai_prediction = round(risk * 100, 2)
            risk_info = get_risk_level_uzbek(risk)
            protocol.risk_level = risk_info['label']
            protocol.save()

            # Update patient medical conditions if found
            if protocol.qand_kasalligi and not patient.qand_kasalligi:
                patient.qand_kasalligi = True
            if protocol.gipertoniya and not patient.gipertoniya:
                patient.gipertoniya = True
            if protocol.yurak_kasalligi and not patient.yurak_kasalligi:
                patient.yurak_kasalligi = True
            patient.save()

            messages.success(request, f"Protokol muvaffaqiyatli yaratildi! AI bashorat: {protocol.ai_prediction}% ({protocol.risk_level})")
            return redirect('protocol_detail', pk=protocol.pk)

        except ValueError as e:
            messages.error(request, f"Ma'lumot formati noto'g'ri: {str(e)}")
        except Exception as e:
            messages.error(request, f"Xato: {str(e)}")

    context = {
        'patient': patient,
    }
    return render(request, 'protocols/protocol_form.html', context)


def protocol_detail(request, pk):
    """View protocol details with AI prediction"""
    protocol = get_object_or_404(Protocol, pk=pk)

    context = {
        'protocol': protocol,
        'patient': protocol.bemor,
    }
    return render(request, 'protocols/protocol_detail.html', context)


@csrf_exempt
def extract_from_transcript(request):
    """API endpoint to extract medical data from transcript using GPT"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            protocol_type = data.get('protocol_type')
            transcript = data.get('transcript')

            if not protocol_type or not transcript:
                return JsonResponse({
                    'success': False,
                    'error': 'protocol_type va transcript kerak'
                }, status=400)

            # Extract data using GPT
            extracted_data = extract_medical_data_from_transcript(protocol_type, transcript)

            if 'error' in extracted_data:
                return JsonResponse({
                    'success': False,
                    'error': extracted_data['error']
                }, status=400)

            return JsonResponse({
                'success': True,
                'data': extracted_data,
                'message': "Ma'lumotlar muvaffaqiyatli ajratib olindi!"
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Noto\'g\'ri JSON format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'POST so\'rov kerak'
    }, status=405)


def get_protocol_schema(request):
    """API endpoint to get JSON schema for a protocol type"""
    protocol_type = request.GET.get('type')
    if not protocol_type:
        return JsonResponse({'error': 'type parametri kerak'}, status=400)

    schema = get_schema_for_protocol(protocol_type)
    return JsonResponse({'schema': schema})


@csrf_exempt
def extract_patient_from_transcript(request):
    """API endpoint to extract patient data from transcript using GPT"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transcript = data.get('transcript')

            if not transcript:
                return JsonResponse({
                    'success': False,
                    'error': 'transcript kerak'
                }, status=400)

            # Extract data using GPT
            extracted_data = extract_patient_data_from_transcript(transcript)

            if 'error' in extracted_data:
                return JsonResponse({
                    'success': False,
                    'error': extracted_data['error']
                }, status=400)

            return JsonResponse({
                'success': True,
                'data': extracted_data,
                'message': "Ma'lumotlar muvaffaqiyatli ajratib olindi!"
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Noto\'g\'ri JSON format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

    return JsonResponse({
        'success': False,
        'error': 'POST so\'rov kerak'
    }, status=405)


def subscriptions(request):
    """Subscriptions page with pricing plans"""
    return render(request, 'subscriptions.html')
