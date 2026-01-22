#!/usr/bin/env python
"""
Script to create realistic demo data for Healthcare CRM
"""
import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'healthcare_crm.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from patients.models import Patient, Appointment, Protocol

# Uzbek names
MALE_NAMES = [
    "Abdulloh Karimov", "Jasur Toshmatov", "Sardor Rahimov", "Bobur Aliyev",
    "Sherzod Nazarov", "Jamshid Usmonov", "Ulugbek Saidov", "Rustam Qodirov",
    "Anvar Ergashev", "Dilshod Mahmudov"
]

FEMALE_NAMES = [
    "Nilufar Karimova", "Gulnora Rahimova", "Madina Aliyeva", "Zarina Toshmatova",
    "Dilnoza Usmonova", "Sevara Nazarova", "Kamola Saidova", "Nodira Qodirova",
    "Shoira Ergasheva", "Lola Mahmudova"
]

DOCTORS = [
    "Dr. Akbar Yusupov", "Dr. Farrux Kamolov", "Dr. Zilola Rahmonova",
    "Dr. Botir Tursunov", "Dr. Gavhar Azizova"
]

DEPARTMENTS = ['terapiya', 'kardiologiya', 'endokrinologiya', 'nevrologiya', 'umumiy']

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

ADDRESSES = [
    "Toshkent sh., Chilonzor tumani",
    "Toshkent sh., Yunusobod tumani",
    "Toshkent sh., Mirzo Ulugbek tumani",
    "Toshkent sh., Sergeli tumani",
    "Toshkent sh., Yakkasaroy tumani",
    "Toshkent sh., Shayxontohur tumani",
    "Samarqand sh., Markaz",
    "Buxoro sh., Markaz",
    "Namangan sh., Markaz",
    "Andijon sh., Markaz"
]

ALLERGIES = [
    "", "", "", "",  # Most people have no allergies
    "Penisilin", "Aspirin", "Sulfanilamidlar",
    "Novokain", "Yod", "Lateks"
]


def clear_data():
    """Clear existing demo data"""
    print("Ma'lumotlarni tozalash...")
    Protocol.objects.all().delete()
    Appointment.objects.all().delete()
    Patient.objects.all().delete()
    print("Barcha ma'lumotlar o'chirildi!")


def create_patients():
    """Create 20 realistic patients with varying health conditions"""
    patients = []

    # Patient profiles with different severity levels
    profiles = [
        # High risk patients (5)
        {"severity": "high", "diabetes": True, "hypertension": True, "heart": True, "age_range": (55, 75)},
        {"severity": "high", "diabetes": True, "hypertension": True, "heart": False, "age_range": (50, 70)},
        {"severity": "high", "diabetes": False, "hypertension": True, "heart": True, "age_range": (60, 80)},
        {"severity": "high", "diabetes": True, "hypertension": False, "heart": True, "age_range": (45, 65)},
        {"severity": "high", "diabetes": True, "hypertension": True, "heart": False, "age_range": (55, 75)},

        # Medium risk patients (7)
        {"severity": "medium", "diabetes": True, "hypertension": False, "heart": False, "age_range": (40, 60)},
        {"severity": "medium", "diabetes": False, "hypertension": True, "heart": False, "age_range": (45, 65)},
        {"severity": "medium", "diabetes": False, "hypertension": False, "heart": True, "age_range": (50, 70)},
        {"severity": "medium", "diabetes": True, "hypertension": False, "heart": False, "age_range": (35, 55)},
        {"severity": "medium", "diabetes": False, "hypertension": True, "heart": False, "age_range": (40, 60)},
        {"severity": "medium", "diabetes": True, "hypertension": True, "heart": False, "age_range": (45, 60)},
        {"severity": "medium", "diabetes": False, "hypertension": False, "heart": True, "age_range": (55, 70)},

        # Low risk patients (8)
        {"severity": "low", "diabetes": False, "hypertension": False, "heart": False, "age_range": (20, 40)},
        {"severity": "low", "diabetes": False, "hypertension": False, "heart": False, "age_range": (25, 45)},
        {"severity": "low", "diabetes": False, "hypertension": False, "heart": False, "age_range": (30, 50)},
        {"severity": "low", "diabetes": False, "hypertension": False, "heart": False, "age_range": (22, 38)},
        {"severity": "low", "diabetes": False, "hypertension": False, "heart": False, "age_range": (28, 42)},
        {"severity": "low", "diabetes": False, "hypertension": False, "heart": False, "age_range": (18, 35)},
        {"severity": "low", "diabetes": False, "hypertension": False, "heart": False, "age_range": (25, 40)},
        {"severity": "low", "diabetes": False, "hypertension": False, "heart": False, "age_range": (30, 45)},
    ]

    all_names = []
    for i in range(10):
        all_names.append((MALE_NAMES[i], "Erkak"))
        all_names.append((FEMALE_NAMES[i], "Ayol"))

    random.shuffle(all_names)

    for i, profile in enumerate(profiles):
        name, gender = all_names[i]
        age = random.randint(*profile["age_range"])

        # Generate phone number
        phone = f"+998 {random.choice(['90', '91', '93', '94', '95', '97', '99'])} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"

        patient = Patient.objects.create(
            ism=name,
            yosh=age,
            jins=gender,
            telefon=phone,
            manzil=random.choice(ADDRESSES),
            qon_guruhi=random.choice(BLOOD_GROUPS),
            allergiyalar=random.choice(ALLERGIES),
            qand_kasalligi=profile["diabetes"],
            gipertoniya=profile["hypertension"],
            yurak_kasalligi=profile["heart"],
            umumiy_uchrashuvlar=random.randint(0, 10),
            kelmaganlar_soni=random.randint(0, 3) if profile["severity"] == "high" else random.randint(0, 1),
        )
        patients.append((patient, profile["severity"]))
        print(f"  Bemor yaratildi: {name} ({profile['severity']} xavf)")

    return patients


def create_appointments(patients):
    """Create appointments for half of the patients"""
    today = timezone.now().date()

    # Select 10 patients for appointments
    patients_with_appointments = random.sample(patients, 10)

    for patient, severity in patients_with_appointments:
        # Create 1-3 appointments per patient
        num_appointments = random.randint(1, 3)

        for j in range(num_appointments):
            # Some appointments today, some in the future, some in the past
            day_offset = random.choice([-7, -3, -1, 0, 0, 0, 1, 3, 7])  # More today
            appointment_date = today + timedelta(days=day_offset)

            # Random time between 9:00 and 17:00
            hour = random.randint(9, 17)
            minute = random.choice([0, 15, 30, 45])

            appointment_datetime = timezone.make_aware(
                datetime.combine(appointment_date, datetime.min.time().replace(hour=hour, minute=minute))
            )

            # Determine status based on date
            if day_offset < 0:
                status = random.choice(['yakunlangan', 'yakunlangan', 'yakunlangan', 'kelmagan'])
            elif day_offset == 0:
                status = 'rejalashtirilgan'
            else:
                status = 'rejalashtirilgan'

            # Risk based on severity
            if severity == "high":
                risk = random.uniform(0.65, 0.95)
            elif severity == "medium":
                risk = random.uniform(0.35, 0.65)
            else:
                risk = random.uniform(0.05, 0.35)

            # Select appropriate department based on conditions
            if patient.yurak_kasalligi:
                dept = 'kardiologiya'
            elif patient.qand_kasalligi:
                dept = 'endokrinologiya'
            elif patient.gipertoniya:
                dept = random.choice(['kardiologiya', 'terapiya'])
            else:
                dept = random.choice(DEPARTMENTS)

            appointment = Appointment.objects.create(
                bemor=patient,
                uchrashuv_sanasi=appointment_datetime,
                shifokor=random.choice(DOCTORS),
                bolim=dept,
                holat=status,
                kelmay_qolish_riski=risk,
                qand_riski=random.uniform(0.2, 0.8) if patient.qand_kasalligi else random.uniform(0.05, 0.3),
                yurak_riski=random.uniform(0.2, 0.8) if patient.yurak_kasalligi else random.uniform(0.05, 0.3),
                sms_yuborildi=random.choice([True, False]),
                izoh="" if random.random() > 0.3 else "Muntazam tekshiruv"
            )

            print(f"    Uchrashuv: {patient.ism} - {appointment_date} ({status})")


def create_protocols(patients):
    """Create protocols for all high risk and most medium risk patients"""

    for patient, severity in patients:
        # High risk patients get 2 protocols, medium get 1, low risk get occasional
        if severity == 'high':
            num_protocols = 2
        elif severity == 'medium':
            num_protocols = 1
        else:
            # Only 2 low risk patients get protocols
            num_protocols = 1 if random.random() < 0.25 else 0

        for _ in range(num_protocols):
            # Determine protocol type based on conditions
            if patient.qand_kasalligi and (not patient.yurak_kasalligi or random.random() < 0.5):
                protocol_type = 'diabetes'
            else:
                protocol_type = 'heart'

            # Risk based on severity
            if severity == 'high':
                risk = random.uniform(0.65, 0.95)
            elif severity == 'medium':
                risk = random.uniform(0.35, 0.65)
            else:
                risk = random.uniform(0.10, 0.35)

            ai_prediction = round(risk * 100, 2)

            if ai_prediction >= 70:
                risk_level = "Yuqori xavf"
            elif ai_prediction >= 30:
                risk_level = "O'rta xavf"
            else:
                risk_level = "Past xavf"

            protocol = Protocol.objects.create(
                bemor=patient,
                protocol_type=protocol_type,
                shifokor=random.choice(DOCTORS),
                qon_guruhi=patient.qon_guruhi,
                allergiyalar=patient.allergiyalar,
                qand_kasalligi=patient.qand_kasalligi,
                gipertoniya=patient.gipertoniya,
                yurak_kasalligi=patient.yurak_kasalligi,
                ai_prediction=ai_prediction,
                risk_level=risk_level,
                izoh="AI tahlili asosida yaratilgan protokol"
            )

            # Add specific fields based on protocol type
            if protocol_type == 'diabetes':
                protocol.pregnancies = random.randint(0, 10) if patient.jins == 'Ayol' else 0
                protocol.glucose = random.uniform(140, 200) if severity == 'high' else random.uniform(100, 140) if severity == 'medium' else random.uniform(70, 100)
                protocol.blood_pressure = random.randint(80, 120)
                protocol.skin_thickness = random.randint(10, 40)
                protocol.insulin = random.uniform(50, 200)
                protocol.bmi = random.uniform(30, 40) if severity == 'high' else random.uniform(25, 32) if severity == 'medium' else random.uniform(20, 26)
                protocol.diabetes_pedigree = random.uniform(0.5, 1.5) if severity == 'high' else random.uniform(0.2, 0.7)
            else:
                protocol.sex = 1 if patient.jins == 'Erkak' else 0
                protocol.chest_pain_type = random.randint(1, 4)
                protocol.resting_bp = random.randint(140, 180) if severity == 'high' else random.randint(120, 150) if severity == 'medium' else random.randint(100, 130)
                protocol.cholesterol = random.uniform(250, 350) if severity == 'high' else random.uniform(200, 260) if severity == 'medium' else random.uniform(150, 210)
                protocol.fasting_blood_sugar = random.choice([True, False])
                protocol.rest_ecg = random.randint(0, 2)
                protocol.max_heart_rate = random.randint(100, 150) if severity == 'high' else random.randint(140, 180)
                protocol.exercise_angina = severity == 'high' and random.random() < 0.7
                protocol.oldpeak = random.uniform(1.5, 4.0) if severity == 'high' else random.uniform(0, 2.0)
                protocol.slope = random.randint(0, 2)
                protocol.num_vessels = random.randint(1, 3) if severity == 'high' else random.randint(0, 1)
                protocol.thal = random.randint(1, 3)

            protocol.save()
            print(f"    Protokol: {patient.ism} - {protocol_type} ({risk_level})")


def main():
    print("=" * 50)
    print("Healthcare CRM Demo Ma'lumotlarini Yaratish")
    print("=" * 50)

    # Clear existing data
    clear_data()

    print("\n1. Bemorlarni yaratish (20 ta)...")
    patients = create_patients()

    print("\n2. Uchrashuvlarni yaratish (10 ta bemor uchun)...")
    create_appointments(patients)

    print("\n3. Protokollarni yaratish...")
    create_protocols(patients)

    print("\n" + "=" * 50)
    print("Demo ma'lumotlar muvaffaqiyatli yaratildi!")
    print("=" * 50)

    # Summary
    print(f"\nXulosa:")
    print(f"  - Jami bemorlar: {Patient.objects.count()}")
    print(f"  - Jami uchrashuvlar: {Appointment.objects.count()}")
    print(f"  - Bugungi uchrashuvlar: {Appointment.objects.filter(uchrashuv_sanasi__date=timezone.now().date()).count()}")
    print(f"  - Protokollar: {Protocol.objects.count()}")
    print(f"  - Yuqori xavfli bemorlar: {Patient.objects.filter(qand_kasalligi=True, gipertoniya=True).count()}")


if __name__ == '__main__':
    main()
