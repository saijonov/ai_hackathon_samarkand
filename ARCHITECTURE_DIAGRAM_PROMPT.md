# Healthcare CRM Architecture Diagram - AI Generation Prompt

## For DALL-E / Midjourney / Stable Diffusion:

```
Create a clean, professional software architecture diagram for a Healthcare CRM system. Use a modern tech style with these exact components:

TOP LAYER (Frontend/User Interface):
- Web Browser with 3 pages: "Dashboard", "Patients", "Appointments"
- Styled with Tailwind CSS (blue theme #0066CC)

MIDDLE LAYER (Django Backend):
- Django 5.0 server box
- 3 Models connected: "Patient Model", "Appointment Model", "HealthScreening Model"
- PostgreSQL/SQLite database cylinder

RIGHT SIDE (Machine Learning Pipeline):
- "Kaggle Datasets" cloud with 3 datasets:
  * No-Show Appointments (110K records)
  * Diabetes Dataset (768 records)
  * Heart Disease Dataset (1025 records)
- Arrow down to "Training Pipeline"
- 3 ML Models in boxes:
  * No-Show Predictor (67.79%)
  * Diabetes Predictor (76.62%)
  * Heart Disease Predictor (98.54%)
- RandomForest + StandardScaler labels

CONNECTIONS:
- Browser arrows to Django
- Django arrows to Database
- Django arrows to ML Models (labeled "predict()")
- Kaggle arrows to ML Models (labeled "train")

COLOR SCHEME:
- Blue (#0066CC) for main components
- Green (#00C853) for ML models
- Orange (#FF9800) for data flow
- Clean white background
- Modern, minimal design

LABELS:
- Add "Python 3.10" badge
- Add "Real-time AI Predictions" badge
- Add "Uzbek Localization" badge

Style: Technical diagram, clean lines, professional, like AWS architecture diagrams
```

## Alternative: Text-Based Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐             │
│  │ Dashboard  │  │  Patients   │  │ Appointments │             │
│  │  /home/    │  │ /patients/  │  │/appointments/│             │
│  └──────┬─────┘  └──────┬──────┘  └──────┬───────┘             │
│         │               │                │                       │
│         └───────────────┴────────────────┘                       │
│                         │                                         │
│                    Tailwind CSS                                   │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO 5.0 BACKEND                            │
│                                                                   │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────┐       │
│  │   Patient    │  │  Appointment  │  │ HealthScreening│       │
│  │    Model     │  │     Model     │  │     Model      │       │
│  │              │  │               │  │                │       │
│  │ - ism        │  │ - bemor       │  │ - bemor        │       │
│  │ - yosh       │  │ - shifokor    │  │ - glyukoza     │       │
│  │ - jins       │  │ - bolim       │  │ - qon_bosimi   │       │
│  │ - qand_kas.  │  │ - holat       │  │ - bmi          │       │
│  └──────┬───────┘  └───────┬───────┘  └────────┬───────┘       │
│         │                  │                    │                │
│         └──────────────────┴────────────────────┘                │
│                            │                                      │
│                            ▼                                      │
│                  ┌─────────────────┐                             │
│                  │  SQLite/PostgreSQL│                            │
│                  │    Database      │                             │
│                  └──────────────────┘                             │
└───────────────────────────┬───────────────────────────────────────┘
                            │
                            │ predict()
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│              MACHINE LEARNING PIPELINE                           │
│                                                                   │
│  TRAINING DATA (Kaggle):                                         │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ • No-Show Appointments  (110,527 records)              │     │
│  │ • Pima Diabetes Dataset (768 records)                  │     │
│  │ • Heart Disease UCI     (1,025 records)                │     │
│  └────────────────┬───────────────────────────────────────┘     │
│                   │                                               │
│                   ▼ train_models_real.py                         │
│                                                                   │
│  TRAINED MODELS:                                                 │
│  ┌──────────────────────┐  ┌─────────────────────┐             │
│  │ No-Show Predictor    │  │ Diabetes Predictor  │             │
│  │ RandomForestClassifier│  │ RandomForestClassifier│            │
│  │ Accuracy: 67.79%     │  │ Accuracy: 76.62%    │             │
│  │ Features: 6          │  │ Features: 8         │             │
│  └──────────────────────┘  └─────────────────────┘             │
│                                                                   │
│  ┌──────────────────────┐                                        │
│  │Heart Disease Predict │                                        │
│  │RandomForestClassifier│                                        │
│  │ Accuracy: 98.54%     │                                        │
│  │ Features: 13         │                                        │
│  └──────────────────────┘                                        │
│                                                                   │
│  PREPROCESSING:                                                  │
│  • StandardScaler for feature normalization                      │
│  • Data cleaning & imputation                                    │
│  • Feature engineering                                           │
└─────────────────────────────────────────────────────────────────┘

DATA FLOW:
1. User creates appointment → Django saves to DB
2. Django calls predict_noshow(patient, appointment)
3. ML model returns risk probability (0-1)
4. Django displays risk with color coding:
   - Green: 0-30% (Past xavf)
   - Orange: 30-70% (O'rta xavf)
   - Red: 70-100% (Yuqori xavf)
```

---

## 🤖 ML Models Summary

### We are using **3 Machine Learning Models**:

1. **No-Show Predictor** (Kelmay qolish bashorati)
   - **Algorithm:** RandomForestClassifier
   - **Accuracy:** 67.79%
   - **Dataset:** 110,527 real medical appointments
   - **Features:** Age, Gender, days_ahead, SMS_received, Hypertension, Diabetes
   - **Output:** Probability patient will miss appointment (0-100%)

2. **Diabetes Predictor** (Qand kasalligi bashorati)
   - **Algorithm:** RandomForestClassifier
   - **Accuracy:** 76.62%
   - **Dataset:** 768 real patient records
   - **Features:** Age, Gender, Glucose, BMI, Blood Pressure
   - **Output:** Probability of diabetes (0-100%)

3. **Heart Disease Predictor** (Yurak kasalligi bashorati)
   - **Algorithm:** RandomForestClassifier
   - **Accuracy:** 98.54%
   - **Dataset:** 1,025 real patient records
   - **Features:** 13 medical features (age, cholesterol, blood pressure, etc.)
   - **Output:** Probability of heart disease (0-100%)

---

## 📍 Where to See Each Model's Results:

### Model 1: No-Show Predictor

**Pages where you can see it:**

1. **Appointments List** - `http://127.0.0.1:8000/appointments/`
   - Column: **"Xavf"** (Risk)
   - Shows: Color-coded badges (🟢 Past / 🟠 O'rta / 🔴 Yuqori xavf)

2. **Dashboard** - `http://127.0.0.1:8000/home/`
   - Section: **"Yuqori Xavfli Bemorlar"** (High-Risk Patients)
   - Shows: Patients with >70% no-show risk

3. **Create Appointment** - `http://127.0.0.1:8000/appointments/create/`
   - After submitting form
   - Shows: Warning message if risk > 70%

4. **Patient Detail** - `http://127.0.0.1:8000/patients/30/`
   - Section: **"Учрашувлар тарихи"** (Appointment History)
   - Shows: "Келмаслик хавфи: X.X%" for each appointment

### Model 2: Diabetes Predictor

**Pages where you can see it:**

1. **Patient Detail** - `http://127.0.0.1:8000/patients/30/`
   - Section: **"AI Sog'liq Tahlili"** (AI Health Analysis)
   - Card: **"Qand kasalligi riski"**
   - Shows: Percentage + Risk Level + Color-coded badge

2. **Health Screening Results** - After creating a screening
   - URL: `http://127.0.0.1:8000/patients/30/screening/`
   - Shows: Real-time diabetes risk calculation based on glucose, BMI

3. **Screening History Table** - `http://127.0.0.1:8000/patients/30/`
   - Section: **"Скрининг тарихи"**
   - Column: **"Қанд хавфи"** (Diabetes Risk)

### Model 3: Heart Disease Predictor

**Pages where you can see it:**

1. **Patient Detail** - `http://127.0.0.1:8000/patients/30/`
   - Section: **"AI Sog'liq Tahlili"**
   - Card: **"Yurak kasalligi riski"**
   - Shows: Percentage + Risk Level + Color-coded badge

2. **Health Screening Results** - After creating a screening
   - URL: `http://127.0.0.1:8000/patients/30/screening/`
   - Shows: Real-time heart disease risk based on blood pressure, cholesterol

3. **Screening History Table** - `http://127.0.0.1:8000/patients/30/`
   - Section: **"Скрининг тарихи"**
   - Column: **"Юрак хавфи"** (Heart Risk)

---

## 🎯 Quick Demo Checklist:

✅ **Dashboard** → See high-risk patients with No-Show Predictor
✅ **Appointments List** → See all 3 model predictions in table
✅ **Patient Detail** → See Diabetes + Heart Disease predictions
✅ **Create Appointment** → See No-Show prediction in real-time
✅ **Add Health Screening** → See all predictions update dynamically

All 3 models are working and visible throughout the system! 🚀
