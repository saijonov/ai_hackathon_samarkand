"""
Training script for healthcare ML models using REAL Kaggle datasets
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os


def create_noshow_model():
    """Train no-show appointment prediction model with REAL data"""
    print("\n=== Training No-Show Prediction Model (REAL DATA) ===")

    # Load real dataset
    df = pd.read_csv('datasets/noshowappointments.csv')
    print(f"Loaded {len(df)} records from Kaggle")

    # Data preprocessing
    # Convert dates
    df['ScheduledDay'] = pd.to_datetime(df['ScheduledDay'])
    df['AppointmentDay'] = pd.to_datetime(df['AppointmentDay'])

    # Calculate days ahead
    df['days_ahead'] = (df['AppointmentDay'] - df['ScheduledDay']).dt.days

    # Filter invalid data
    df = df[df['days_ahead'] >= 0]

    # Convert Gender to numeric
    df['Gender'] = df['Gender'].map({'M': 1, 'F': 0})

    # Convert No-show to numeric (Yes=1, No=0)
    df['No-show'] = df['No-show'].map({'Yes': 1, 'No': 0})

    # Convert SMS_received to int
    df['SMS_received'] = df['SMS_received'].astype(int)

    # Select features (note: Hipertension not Hypertension in this dataset)
    features = ['Age', 'Gender', 'days_ahead', 'SMS_received', 'Hipertension', 'Diabetes']
    X = df[features].fillna(0)
    y = df['No-show']

    print(f"Training on {len(X)} samples with {len(features)} features")

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✓ No-Show Model Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Will Attend', 'Will Miss']))

    # Save model and scaler
    joblib.dump(model, 'ml_models/noshow_predictor.pkl')
    joblib.dump(scaler, 'ml_models/noshow_scaler.pkl')
    print("✓ Model saved: noshow_predictor.pkl")

    return accuracy


def create_diabetes_model():
    """Train diabetes prediction model with REAL data"""
    print("\n=== Training Diabetes Prediction Model (REAL DATA) ===")

    # Load real dataset
    df = pd.read_csv('datasets/diabetes.csv')
    print(f"Loaded {len(df)} records from Kaggle")

    # Features and target
    feature_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
                    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    X = df[feature_cols]
    y = df['Outcome']

    # Replace zeros with median (medical impossibility)
    cols_to_fix = ['Glucose', 'BloodPressure', 'BMI']
    for col in cols_to_fix:
        X[col] = X[col].replace(0, X[col].median())

    print(f"Training on {len(X)} samples with {len(feature_cols)} features")

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✓ Diabetes Model Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Diabetes', 'Has Diabetes']))

    # Save model and scaler
    joblib.dump(model, 'ml_models/diabetes_predictor.pkl')
    joblib.dump(scaler, 'ml_models/diabetes_scaler.pkl')
    print("✓ Model saved: diabetes_predictor.pkl")

    return accuracy


def create_heart_disease_model():
    """Train heart disease prediction model with REAL data"""
    print("\n=== Training Heart Disease Prediction Model (REAL DATA) ===")

    # Load real dataset
    df = pd.read_csv('datasets/heart.csv')
    print(f"Loaded {len(df)} records from Kaggle")

    # Features and target
    X = df.drop('target', axis=1)
    y = df['target']

    print(f"Training on {len(X)} samples with {len(X.columns)} features")

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✓ Heart Disease Model Accuracy: {accuracy:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Disease', 'Has Disease']))

    # Save model and scaler
    joblib.dump(model, 'ml_models/heart_predictor.pkl')
    joblib.dump(scaler, 'ml_models/heart_scaler.pkl')
    print("✓ Model saved: heart_predictor.pkl")

    return accuracy


if __name__ == '__main__':
    print("=" * 60)
    print("Healthcare CRM - ML Model Training with REAL DATA")
    print("=" * 60)

    # Train all models
    noshow_acc = create_noshow_model()
    diabetes_acc = create_diabetes_model()
    heart_acc = create_heart_disease_model()

    print("\n" + "=" * 60)
    print("Training Complete with REAL Kaggle Data!")
    print("=" * 60)
    print(f"✓ No-Show Model:      {noshow_acc:.2%} accuracy")
    print(f"✓ Diabetes Model:     {diabetes_acc:.2%} accuracy")
    print(f"✓ Heart Disease Model: {heart_acc:.2%} accuracy")
    print("\nAll models saved in ml_models/ directory")
    print("Models are now ready to use in the Healthcare CRM system!")
    print("=" * 60)
