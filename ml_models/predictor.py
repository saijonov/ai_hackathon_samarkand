"""
ML Prediction Service for Healthcare CRM
Loads trained models and provides prediction functions
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
        # Return default prediction if models not loaded
        return 0.3

    try:
        # Prepare features: [Age, Gender, days_ahead, SMS_received, Hypertension, Diabetes]
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

        # Scale and predict
        features_scaled = noshow_scaler.transform(features)
        probability = noshow_model.predict_proba(features_scaled)[0][1]

        return round(probability, 3)
    except Exception as e:
        print(f"Error in predict_noshow: {e}")
        return 0.3


def predict_diabetes(patient, glucose=None, bmi=None, blood_pressure=None):
    """
    Predict probability of diabetes

    Args:
        patient: Patient object
        glucose: Blood glucose level (optional, will estimate if None)
        bmi: Body Mass Index (optional, will estimate if None)
        blood_pressure: Blood pressure (optional, will estimate if None)

    Returns:
        float: Probability of diabetes (0-1)
    """
    if not MODELS_LOADED:
        return 0.2

    try:
        # Use provided values or estimate based on age and conditions
        if glucose is None:
            # Estimate glucose based on age and diabetes history
            glucose = 100 + (patient.yosh - 40) * 0.5
            if patient.qand_kasalligi:
                glucose += 40

        if bmi is None:
            # Estimate BMI based on age
            bmi = 25 + (patient.yosh - 40) * 0.1

        if blood_pressure is None:
            # Estimate blood pressure
            blood_pressure = 70 + (patient.yosh - 30) * 0.3
            if patient.gipertoniya:
                blood_pressure += 15

        gender_code = 1 if patient.jins == 'E' else 0

        features = np.array([[
            patient.yosh,
            gender_code,
            glucose,
            bmi,
            blood_pressure
        ]])

        features_scaled = diabetes_scaler.transform(features)
        probability = diabetes_model.predict_proba(features_scaled)[0][1]

        return round(probability, 3)
    except Exception as e:
        print(f"Error in predict_diabetes: {e}")
        return 0.2


def predict_heart_disease(patient, blood_pressure=None, cholesterol=None, max_heart_rate=None):
    """
    Predict probability of heart disease

    Args:
        patient: Patient object
        blood_pressure: Systolic blood pressure (optional)
        cholesterol: Cholesterol level (optional)
        max_heart_rate: Maximum heart rate (optional)

    Returns:
        float: Probability of heart disease (0-1)
    """
    if not MODELS_LOADED:
        return 0.25

    try:
        # Estimate values if not provided
        if blood_pressure is None:
            blood_pressure = 120 + (patient.yosh - 40) * 0.5
            if patient.gipertoniya:
                blood_pressure += 20

        if cholesterol is None:
            cholesterol = 180 + (patient.yosh - 40) * 1.5

        if max_heart_rate is None:
            max_heart_rate = 220 - patient.yosh - (10 if patient.yurak_kasalligi else 0)

        gender_code = 1 if patient.jins == 'E' else 0

        features = np.array([[
            patient.yosh,
            gender_code,
            blood_pressure,
            cholesterol,
            max_heart_rate
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
