"""
ML Prediction Service for Healthcare CRM
Loads trained models and provides prediction functions

Dataset Features:
- Diabetes: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
- Heart: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
"""

import joblib
import numpy as np
import os

# Get the directory where models are stored
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load models when module is imported
try:
    noshow_model = joblib.load(os.path.join(BASE_DIR, 'noshow_predictor.pkl'))
    noshow_scaler = joblib.load(os.path.join(BASE_DIR, 'noshow_scaler.pkl'))

    diabetes_model = joblib.load(os.path.join(BASE_DIR, 'diabetes_predictor.pkl'))
    diabetes_scaler = joblib.load(os.path.join(BASE_DIR, 'diabetes_scaler.pkl'))

    heart_model = joblib.load(os.path.join(BASE_DIR, 'heart_predictor.pkl'))
    heart_scaler = joblib.load(os.path.join(BASE_DIR, 'heart_scaler.pkl'))

    MODELS_LOADED = True
    print("✓ ML Models loaded successfully")
except Exception as e:
    MODELS_LOADED = False
    print(f"Warning: Could not load ML models: {e}")


def predict_noshow(patient, appointment):
    """
    Predict probability that patient will miss appointment

    Args:
        patient: Patient object with age, gender, chronic conditions
        appointment: Appointment object with days_ahead calculation

    Returns:
        float: Probability of no-show (0-1)
    """
    if not MODELS_LOADED:
        return 0.3

    try:
        # Features: [Age, Gender, days_ahead, SMS_received, Hypertension, Diabetes]
        gender_code = 1 if patient.jins == 'E' else 0
        days_ahead = appointment.kunlar_farqi() if hasattr(appointment, 'kunlar_farqi') else 5
        sms_received = 1 if appointment.sms_yuborildi else 0
        hypertension = 1 if patient.gipertoniya else 0
        diabetes = 1 if patient.qand_kasalligi else 0

        features = np.array([[
            patient.yosh,
            gender_code,
            days_ahead,
            sms_received,
            hypertension,
            diabetes
        ]])

        features_scaled = noshow_scaler.transform(features)
        probability = noshow_model.predict_proba(features_scaled)[0][1]

        return round(probability, 3)
    except Exception as e:
        print(f"Error in predict_noshow: {e}")
        return 0.3


def predict_diabetes_from_protocol(protocol):
    """
    Predict probability of diabetes from protocol data.
    Uses all 8 features from Kaggle Pima Indians Diabetes dataset.

    Feature order: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age

    Args:
        protocol: Protocol object with all diabetes fields

    Returns:
        float: Probability of diabetes (0-1)
    """
    if not MODELS_LOADED:
        return 0.2

    try:
        # Get patient age from related patient (field is 'bemor' in Django model)
        patient_age = protocol.bemor.yosh if protocol.bemor else 35

        # Extract features in the exact order the model was trained
        # Features: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
        features = np.array([[
            protocol.pregnancies if protocol.pregnancies is not None else 0,
            protocol.glucose if protocol.glucose is not None else 100,
            protocol.blood_pressure if protocol.blood_pressure is not None else 70,
            protocol.skin_thickness if protocol.skin_thickness is not None else 20,
            protocol.insulin if protocol.insulin is not None else 80,
            protocol.bmi if protocol.bmi is not None else 25,
            protocol.diabetes_pedigree if protocol.diabetes_pedigree is not None else 0.5,
            patient_age
        ]])

        features_scaled = diabetes_scaler.transform(features)
        probability = diabetes_model.predict_proba(features_scaled)[0][1]

        return round(probability, 3)
    except Exception as e:
        print(f"Error in predict_diabetes_from_protocol: {e}")
        return 0.2


def predict_heart_disease_from_protocol(protocol):
    """
    Predict probability of heart disease from protocol data.
    Uses all 13 features from Kaggle Heart Disease dataset.

    Feature order: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal

    Args:
        protocol: Protocol object with all heart disease fields

    Returns:
        float: Probability of heart disease (0-1)
    """
    if not MODELS_LOADED:
        return 0.25

    try:
        # Get patient info from related patient (field is 'bemor' in Django model)
        patient = protocol.bemor
        patient_age = patient.yosh if patient else 50
        # sex: 1 = male (Erkak), 0 = female (Ayol)
        patient_sex = 1 if patient and patient.jins == 'E' else 0

        # Extract features in the exact order the model was trained
        # Features: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
        features = np.array([[
            patient_age,                                                                      # age
            protocol.sex if protocol.sex is not None else patient_sex,                        # sex (0=F, 1=M)
            protocol.chest_pain_type if protocol.chest_pain_type is not None else 0,          # cp (chest pain type 0-3)
            protocol.resting_bp if protocol.resting_bp is not None else 120,                  # trestbps (resting blood pressure)
            protocol.cholesterol if protocol.cholesterol is not None else 200,                # chol (cholesterol)
            1 if protocol.fasting_blood_sugar else 0,                                         # fbs (fasting blood sugar > 120)
            protocol.rest_ecg if protocol.rest_ecg is not None else 0,                        # restecg (resting ECG 0-2)
            protocol.max_heart_rate if protocol.max_heart_rate is not None else 150,          # thalach (max heart rate)
            1 if protocol.exercise_angina else 0,                                             # exang (exercise angina)
            protocol.oldpeak if protocol.oldpeak is not None else 1.0,                        # oldpeak (ST depression)
            protocol.slope if protocol.slope is not None else 1,                              # slope (ST segment slope 0-2)
            protocol.num_vessels if protocol.num_vessels is not None else 0,                  # ca (number of major vessels 0-3)
            protocol.thal if protocol.thal is not None else 2                                 # thal (thalassemia 1-3)
        ]])

        features_scaled = heart_scaler.transform(features)
        probability = heart_model.predict_proba(features_scaled)[0][1]

        return round(probability, 3)
    except Exception as e:
        print(f"Error in predict_heart_disease_from_protocol: {e}")
        return 0.25


# Keep old functions for backward compatibility (for patient-based predictions without protocols)
def predict_diabetes(patient, glucose=None, bmi=None, blood_pressure=None):
    """
    Legacy function - Predict probability of diabetes from basic patient data.
    For more accurate predictions, use predict_diabetes_from_protocol() with a protocol object.
    """
    if not MODELS_LOADED:
        return 0.2

    try:
        if glucose is None:
            glucose = 100 + (patient.yosh - 40) * 0.5
            if patient.qand_kasalligi:
                glucose += 40
        if bmi is None:
            bmi = 25 + (patient.yosh - 40) * 0.1
        if blood_pressure is None:
            blood_pressure = 70 + (patient.yosh - 30) * 0.3
            if patient.gipertoniya:
                blood_pressure += 15

        # Use default values for missing protocol fields
        features = np.array([[
            0,                    # Pregnancies (default)
            glucose,              # Glucose
            blood_pressure,       # BloodPressure
            20,                   # SkinThickness (default)
            80,                   # Insulin (default)
            bmi,                  # BMI
            0.5,                  # DiabetesPedigreeFunction (default)
            patient.yosh          # Age
        ]])

        features_scaled = diabetes_scaler.transform(features)
        probability = diabetes_model.predict_proba(features_scaled)[0][1]

        return round(probability, 3)
    except Exception as e:
        print(f"Error in predict_diabetes: {e}")
        return 0.2


def predict_heart_disease(patient, blood_pressure=None, cholesterol=None, max_heart_rate=None):
    """
    Legacy function - Predict probability of heart disease from basic patient data.
    For more accurate predictions, use predict_heart_disease_from_protocol() with a protocol object.
    """
    if not MODELS_LOADED:
        return 0.25

    try:
        if blood_pressure is None:
            blood_pressure = 120 + (patient.yosh - 40) * 0.5
            if patient.gipertoniya:
                blood_pressure += 20
        if cholesterol is None:
            cholesterol = 180 + (patient.yosh - 40) * 1.5
        if max_heart_rate is None:
            max_heart_rate = 220 - patient.yosh - (10 if patient.yurak_kasalligi else 0)

        gender_code = 1 if patient.jins == 'E' else 0

        # Use default values for missing protocol fields
        features = np.array([[
            patient.yosh,        # age
            gender_code,         # sex
            0,                   # cp (default)
            blood_pressure,      # trestbps
            cholesterol,         # chol
            0,                   # fbs (default)
            0,                   # restecg (default)
            max_heart_rate,      # thalach
            0,                   # exang (default)
            1.0,                 # oldpeak (default)
            1,                   # slope (default)
            0,                   # ca (default)
            2                    # thal (default)
        ]])

        features_scaled = heart_scaler.transform(features)
        probability = heart_model.predict_proba(features_scaled)[0][1]

        return round(probability, 3)
    except Exception as e:
        print(f"Error in predict_heart_disease: {e}")
        return 0.25


def get_risk_level_uzbek(probability):
    """
    Convert probability to risk level with Uzbek labels

    Args:
        probability: float between 0 and 1

    Returns:
        dict with level, label, color, and badge_class
    """
    if probability < 0.3:
        return {
            'level': 'past',
            'label': 'Past xavf',
            'color': '#00C853',
            'badge_class': 'badge-success',
            'percentage': f"{probability * 100:.1f}%"
        }
    elif probability < 0.7:
        return {
            'level': 'orta',
            'label': "O'rta xavf",
            'color': '#FF9800',
            'badge_class': 'badge-warning',
            'percentage': f"{probability * 100:.1f}%"
        }
    else:
        return {
            'level': 'yuqori',
            'label': 'Yuqori xavf',
            'color': '#FF6B6B',
            'badge_class': 'badge-danger',
            'percentage': f"{probability * 100:.1f}%"
        }


def get_risk_percentage(probability):
    """Format probability as percentage string"""
    return f"{probability * 100:.1f}%"
