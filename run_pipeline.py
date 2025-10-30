#!/usr/bin/env python3
"""
GenomeGuard Pipeline Runner
Complete workflow for genetic disease risk prediction
"""

import os
import sys
import subprocess

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"STEP: {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    print("🧬 GenomeGuard - AI Genetic Disease Predictor")
    print("Starting complete analysis pipeline...")
    
    # Check if sample VCF exists
    if not os.path.exists("data/raw/sample.vcf"):
        print("❌ No VCF file found in data/raw/")
        print("Please place your VCF file in data/raw/ directory")
        return
    
    # Step 1: Preprocess VCF
    if not run_command("python scripts/preprocess.py", "Preprocessing VCF files"):
        return
    
    # Step 2: Annotate variants
    if not run_command("python scripts/annotate.py", "Annotating variants"):
        return
    
    # Step 3: Train model (if not exists)
    if not os.path.exists("models/model.pkl"):
        if not run_command("python scripts/train.py", "Training ML model"):
            return
    else:
        print("\n✅ Model already exists, skipping training")
    
    # Step 4: Predict disease risk
    if not run_command("python scripts/predict.py sample.vcf", "Predicting disease risk"):
        return
    
    print(f"\n{'='*50}")
    print("🎉 PIPELINE COMPLETE!")
    print("{'='*50}")
    print("Next steps:")
    print("1. Run 'streamlit run app/dashboard.py' to view results")
    print("2. Check data/processed/ for intermediate files")
    print("3. Upload your own VCF files to data/raw/")

if __name__ == "__main__":
    main()