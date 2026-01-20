#!/usr/bin/env python3
"""
Download medical datasets from Kaggle
Run this after setting up kaggle.json credentials
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"stderr: {e.stderr}")
        return False

def main():
    # Change to datasets directory
    os.makedirs('datasets', exist_ok=True)
    os.chdir('datasets')

    print("\n" + "="*60)
    print("Healthcare CRM - Kaggle Dataset Downloader")
    print("="*60)

    # Check if kaggle is configured
    print("\nChecking Kaggle credentials...")
    if not os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json')):
        print("❌ Error: kaggle.json not found!")
        print("\nPlease follow these steps:")
        print("1. Go to https://www.kaggle.com/settings/account")
        print("2. Click 'Create New API Token'")
        print("3. Run these commands:")
        print("   mkdir -p ~/.kaggle")
        print("   mv ~/Downloads/kaggle.json ~/.kaggle/")
        print("   chmod 600 ~/.kaggle/kaggle.json")
        sys.exit(1)

    print("✓ kaggle.json found")

    # Dataset 1: No-Show Appointments
    print("\n\n📥 Downloading Dataset 1: Medical Appointment No-Shows")
    if run_command(
        'kaggle datasets download -d joniarroba/noshowappointments --unzip',
        'Downloading No-Show Appointments dataset...'
    ):
        # Rename the file
        if os.path.exists('KaggleV2-May-2016.csv'):
            os.rename('KaggleV2-May-2016.csv', 'noshowappointments.csv')
            print("✓ Saved as: noshowappointments.csv")

    # Dataset 2: Diabetes
    print("\n\n📥 Downloading Dataset 2: Pima Indians Diabetes")
    if run_command(
        'kaggle datasets download -d uciml/pima-indians-diabetes-database --unzip',
        'Downloading Diabetes dataset...'
    ):
        print("✓ Saved as: diabetes.csv")

    # Dataset 3: Heart Disease
    print("\n\n📥 Downloading Dataset 3: Heart Disease UCI")
    if run_command(
        'kaggle datasets download -d ronitf/heart-disease-uci --unzip',
        'Downloading Heart Disease dataset...'
    ):
        print("✓ Saved as: heart.csv")

    # Clean up
    print("\n\n🧹 Cleaning up zip files...")
    for file in os.listdir('.'):
        if file.endswith('.zip'):
            os.remove(file)
            print(f"  Removed: {file}")

    # Summary
    print("\n" + "="*60)
    print("Download Summary")
    print("="*60)

    files = {
        'noshowappointments.csv': 'No-Show Appointments',
        'diabetes.csv': 'Pima Indians Diabetes',
        'heart.csv': 'Heart Disease UCI'
    }

    for filename, name in files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename) / (1024 * 1024)  # MB
            print(f"✓ {name:30s} - {size:.2f} MB")
        else:
            print(f"✗ {name:30s} - NOT FOUND")

    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Run: python3 ml_models/train_models_real.py")
    print("2. This will train models with real data")
    print("3. Models will be saved in ml_models/ folder")
    print("\n✅ Done!")

if __name__ == '__main__':
    main()
