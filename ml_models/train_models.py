"""
Training script for healthcare ML models
Uses real Kaggle datasets for training
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
    """Train no-show appointment prediction model using synthetic data"""
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
    noshow_prob = (
        (age < 30) * 0.2 +
        (1 - sms_received) * 0.3 +
        (days_ahead > 15) * 0.2 +
        hypertension * 0.15 +
        diabetes * 0.15
    )
    noshow = (np.random.random(n_samples) < noshow_prob).astype(int)

    df = pd.DataFrame({
        'Age': age,
        'Gender': gender,
        'days_ahead': days_ahead,
        'SMS_received': sms_received,
        'Hypertension': hypertension,
        'Diabetes': diabetes,
        'No_show': noshow
    })

    X = df.drop('No_show', axis=1)
    y = df['No_show']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"No-Show Model Accuracy: {accuracy:.2%}")

    joblib.dump(model, 'ml_models/noshow_predictor.pkl')
    joblib.dump(scaler, 'ml_models/noshow_scaler.pkl')
    print("✓ Model saved: noshow_predictor.pkl")

    return accuracy


def create_diabetes_model():
    """Train diabetes prediction model using Kaggle dataset"""
    print("\n=== Training Diabetes Prediction Model ===")
    print("Using Kaggle Pima Indians Diabetes dataset")

    # Load actual dataset
    df = pd.read_csv('datasets/diabetes.csv')
    print(f"Dataset loaded: {len(df)} records")
    print(f"Features: {list(df.columns)}")

    # Features: Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
    # Target: Outcome (1=diabetes, 0=no diabetes)
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']

    print(f"Feature columns: {list(X.columns)}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Diabetes Model Accuracy: {accuracy:.2%}")

    # Save feature names for reference
    feature_names = list(X.columns)
    print(f"Feature order: {feature_names}")

    joblib.dump(model, 'ml_models/diabetes_predictor.pkl')
    joblib.dump(scaler, 'ml_models/diabetes_scaler.pkl')
    joblib.dump(feature_names, 'ml_models/diabetes_features.pkl')
    print("✓ Model saved: diabetes_predictor.pkl")

    return accuracy


def create_heart_disease_model():
    """Train heart disease prediction model using Kaggle dataset"""
    print("\n=== Training Heart Disease Prediction Model ===")
    print("Using Kaggle Heart Disease dataset")

    # Load actual dataset
    df = pd.read_csv('datasets/heart.csv')
    print(f"Dataset loaded: {len(df)} records")
    print(f"Features: {list(df.columns)}")

    # Features: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
    # Target: target (1=heart disease, 0=no disease)
    X = df.drop('target', axis=1)
    y = df['target']

    print(f"Feature columns: {list(X.columns)}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)
    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Heart Disease Model Accuracy: {accuracy:.2%}")

    # Save feature names for reference
    feature_names = list(X.columns)
    print(f"Feature order: {feature_names}")

    joblib.dump(model, 'ml_models/heart_predictor.pkl')
    joblib.dump(scaler, 'ml_models/heart_scaler.pkl')
    joblib.dump(feature_names, 'ml_models/heart_features.pkl')
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
