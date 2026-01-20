"""
Generate demo data for Healthcare CRM
Run with: python3 manage.py shell < generate_demo_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_crm.settings')
django.setup()

from patients.models import Patient, Appointment, HealthScreening
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Clear existing data
print("Clearing existing data...")
HealthScreening.objects.all().delete()
Appointment.objects.all().delete()
Patient.objects.all().delete()

# Uzbek names
uzbek_names_male = [
    "Ahmad Karimov", "Javohir Toshmatov", "Bekzod Rahimov", "Otabek Umarov",
    "Sardor Qodirov", "Aziz Yo'ldoshev", "Jasur Aliyev", "Timur Sharipov",
    "Sanjar Ergashev", "Dilshod Najmiddinov", "Akmal Yusupov", "Rustam Niyozov"
]

uzbek_names_female = [
    "Zebo Abdullayeva", "Malika Ibragimova", "Dilnoza Hasanova", "Nigora Sultonova",
    "Aziza Rahmonova", "Feruza Ismoilova", "Nodira Karimova", "Gulnora Abdullaeva",
    "Dilfuza Mahmudova", "Sevara Usmonova"
]

shifokor_names = [
    "Dr. Ali Alimov", "Dr. Olim Qosimov", "Dr. Madina Yusupova", "Dr. Shoxrux Rahimov",
    "Dr. Nilufar Karimova", "Dr. Bahrom Ergashev", "Dr. Zilola Toshmatova"
]

bolimlar = ['terapiya', 'kardiologiya', 'endokrinologiya', 'nevrologiya', 'pediatriya']

print("Creating patients...")
patients = []

for i in range(30):
    is_male = i < 17
    name = random.choice(uzbek_names_male if is_male else uzbek_names_female)
    district = random.choice(['Chilonzor', 'Yunusobod', 'Olmazor', 'Mirzo Ulugbek', 'Yakkasaroy'])

    patient = Patient.objects.create(
        ism=name,
        yosh=random.randint(20, 75),
        jins='E' if is_male else 'A',
        telefon=f"+998{random.randint(90,99)}{random.randint(1000000,9999999)}",
        manzil=f"Toshkent, {district} tumani",
        qon_guruhi=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
        qand_kasalligi=random.choice([True, False]),
        gipertoniya=random.choice([True, False]),
        yurak_kasalligi=random.choice([True, False]),
    )
    patients.append(patient)
    print(f"  Created: {patient.ism}")

print(f"\n✓ Created {len(patients)} patients")

# Import ML predictor
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ml_models.predictor import predict_noshow, predict_diabetes, predict_heart_disease

print("\nCreating appointments...")
appointments_created = 0

for patient in patients:
    # Create 1-3 appointments per patient
    num_appointments = random.randint(1, 3)

    for j in range(num_appointments):
        # Random date within next 14 days or past 7 days
        days_offset = random.randint(-7, 14)
        appointment_date = timezone.now() + timedelta(days=days_offset, hours=random.randint(8, 17))

        # Determine status based on date
        if days_offset < 0:
            # Past appointment
            holat = random.choice(['yakunlangan', 'yakunlangan', 'yakunlangan', 'kelmagan'])
        else:
            holat = 'rejalashtirilgan'

        appointment = Appointment.objects.create(
            bemor=patient,
            uchrashuv_sanasi=appointment_date,
            shifokor=random.choice(shifokor_names),
            bolim=random.choice(bolimlar),
            sms_yuborildi=random.choice([True, False]),
            holat=holat,
        )

        # Calculate AI predictions
        try:
            noshow_risk = predict_noshow(patient, appointment)
            diabetes_risk = predict_diabetes(patient)
            heart_risk = predict_heart_disease(patient)

            appointment.kelmay_qolish_riski = noshow_risk
            appointment.qand_riski = diabetes_risk
            appointment.yurak_riski = heart_risk
            appointment.save()
        except:
            pass

        # Update patient stats
        patient.umumiy_uchrashuvlar += 1
        if holat == 'kelmagan':
            patient.kelmaganlar_soni += 1

        appointments_created += 1

# Save all patients with updated stats
for patient in patients:
    patient.save()

print(f"✓ Created {appointments_created} appointments")

# Create some health screenings
print("\nCreating health screenings...")
screenings_created = 0

for patient in random.sample(patients, 10):
    screening = HealthScreening.objects.create(
        bemor=patient,
        qon_bosimi_yuqori=random.randint(110, 160),
        qon_bosimi_past=random.randint(70, 95),
        puls=random.randint(60, 100),
        harorat=round(random.uniform(36.4, 37.2), 1),
        glyukoza=round(random.uniform(80, 180), 1),
        holesterin=round(random.uniform(150, 250), 1),
        bmi=round(random.uniform(20, 35), 1),
    )

    # Calculate AI predictions
    try:
        diabetes_risk = predict_diabetes(
            patient,
            glucose=screening.glyukoza,
            bmi=screening.bmi,
            blood_pressure=screening.qon_bosimi_past
        )
        heart_risk = predict_heart_disease(
            patient,
            blood_pressure=screening.qon_bosimi_yuqori,
            cholesterol=screening.holesterin
        )

        screening.qand_ehtimoli = diabetes_risk
        screening.yurak_ehtimoli = heart_risk
        screening.save()
    except:
        pass

    screenings_created += 1

print(f"✓ Created {screenings_created} health screenings")

print("\n" + "="*60)
print("Demo Data Generation Complete!")
print("="*60)
print(f"Patients: {Patient.objects.count()}")
print(f"Appointments: {Appointment.objects.count()}")
print(f"Health Screenings: {HealthScreening.objects.count()}")
print("\nYou can now login to the system!")
print("="*60)
