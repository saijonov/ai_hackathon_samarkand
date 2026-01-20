"""
Training script for healthcare ML models
Creates synthetic data and trains RandomForest classifiers
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os


def create_noshow_model():
    """Train no-show appointment prediction model"""
    print("\n=== Training No-Show Prediction Model ===")

    # Generate synthetic data (1000 samples)
    np.random.seed(42)
    n_samples = 1000

    # Features: Age, Gender (0=F, 1=M), Days_ahead, SMS_received, Hypertension, Diabetes
    age = np.random.randint(18, 80, n_samples)
    gender = np.random.randint(0, 2, n_samples)
    days_ahead = np.random.randint(0, 30, n_samples)
    sms_received = np.random.randint(0, 2, n_samples)
    hypertension = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
    diabetes = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])

    # Target: No-show (1=missed, 0=attended)
    # Logic: Higher risk if: young age, no SMS, many days ahead, chronic conditions
    noshow_prob = (
        (age < 30) * 0.2 +
        (1 - sms_received) * 0.3 +
        (days_ahead > 15) * 0.2 +
        hypertension * 0.15 +
        diabetes * 0.15
    )
    noshow = (np.random.random(n_samples) < noshow_prob).astype(int)

    # Create dataframe
    df = pd.DataFrame({
        'Age': age,
        'Gender': gender,
        'days_ahead': days_ahead,
        'SMS_received': sms_received,
        'Hypertension': hypertension,
        'Diabetes': diabetes,
        'No_show': noshow
    })

    # Split features and target
    X = df.drop('No_show', axis=1)
    y = df['No_show']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"No-Show Model Accuracy: {accuracy:.2%}")

    # Save model and scaler
    joblib.dump(model, 'ml_models/noshow_predictor.pkl')
    joblib.dump(scaler, 'ml_models/noshow_scaler.pkl')
    print("✓ Model saved: noshow_predictor.pkl")

    return accuracy


def create_diabetes_model():
    """Train diabetes prediction model"""
    print("\n=== Training Diabetes Prediction Model ===")

    np.random.seed(43)
    n_samples = 1000

    # Features: Age, Gender, Glucose, BMI
    age = np.random.randint(25, 80, n_samples)
    gender = np.random.randint(0, 2, n_samples)
    glucose = np.random.normal(120, 30, n_samples)
    bmi = np.random.normal(28, 6, n_samples)
    blood_pressure = np.random.normal(80, 15, n_samples)

    # Target: Diabetes (1=has diabetes, 0=no diabetes)
    # Logic: Higher risk if: older, high glucose, high BMI
    diabetes_prob = (
        (age > 50) * 0.2 +
        (glucose > 140) * 0.4 +
        (bmi > 30) * 0.25 +
        (blood_pressure > 90) * 0.15
    )
    diabetes = (np.random.random(n_samples) < diabetes_prob).astype(int)

    df = pd.DataFrame({
        'Age': age,
        'Gender': gender,
        'Glucose': glucose,
        'BMI': bmi,
        'BloodPressure': blood_pressure,
        'Diabetes': diabetes
    })

    X = df.drop('Diabetes', axis=1)
    y = df['Diabetes']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Diabetes Model Accuracy: {accuracy:.2%}")

    joblib.dump(model, 'ml_models/diabetes_predictor.pkl')
    joblib.dump(scaler, 'ml_models/diabetes_scaler.pkl')
    print("✓ Model saved: diabetes_predictor.pkl")

    return accuracy


def create_heart_disease_model():
    """Train heart disease prediction model"""
    print("\n=== Training Heart Disease Prediction Model ===")

    np.random.seed(44)
    n_samples = 1000

    # Features: Age, Gender, Blood Pressure, Cholesterol, Max Heart Rate
    age = np.random.randint(30, 80, n_samples)
    gender = np.random.randint(0, 2, n_samples)
    blood_pressure = np.random.normal(130, 20, n_samples)
    cholesterol = np.random.normal(220, 40, n_samples)
    max_heart_rate = np.random.normal(150, 25, n_samples)

    # Target: Heart Disease (1=has disease, 0=no disease)
    heart_disease_prob = (
        (age > 55) * 0.25 +
        (blood_pressure > 140) * 0.25 +
        (cholesterol > 240) * 0.25 +
        (max_heart_rate < 120) * 0.25
    )
    heart_disease = (np.random.random(n_samples) < heart_disease_prob).astype(int)

    df = pd.DataFrame({
        'Age': age,
        'Gender': gender,
        'BloodPressure': blood_pressure,
        'Cholesterol': cholesterol,
        'MaxHeartRate': max_heart_rate,
        'HeartDisease': heart_disease
    })

    X = df.drop('HeartDisease', axis=1)
    y = df['HeartDisease']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Heart Disease Model Accuracy: {accuracy:.2%}")

    joblib.dump(model, 'ml_models/heart_predictor.pkl')
    joblib.dump(scaler, 'ml_models/heart_scaler.pkl')
    print("✓ Model saved: heart_predictor.pkl")

    return accuracy


if __name__ == '__main__':
    print("=" * 60)
    print("Healthcare CRM - ML Model Training")
    print("=" * 60)

    # Create models directory if it doesn't exist
    os.makedirs('ml_models', exist_ok=True)

    # Train all models
    noshow_acc = create_noshow_model()
    diabetes_acc = create_diabetes_model()
    heart_acc = create_heart_disease_model()

    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"No-Show Model: {noshow_acc:.2%} accuracy")
    print(f"Diabetes Model: {diabetes_acc:.2%} accuracy")
    print(f"Heart Disease Model: {heart_acc:.2%} accuracy")
    print("\nAll models saved in ml_models/ directory")
