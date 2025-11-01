import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import pickle
import os

def create_features(df):
    """Extract features from annotated variants"""
    features = []
    
    # Count variants by risk level
    risk_counts = df['DISEASE_RISK'].value_counts()
    high_risk = risk_counts.get('High', 0)
    medium_risk = risk_counts.get('Medium', 0)
    low_risk = risk_counts.get('Low', 0)
    
    # Count pathogenic variants
    pathogenic_count = len(df[df['PATHOGENICITY'] == 'Pathogenic'])
    
    # Quality metrics
    avg_quality = df['QUAL'].mean() if 'QUAL' in df.columns else 0
    
    # Gene-specific counts
    brca_variants = len(df[df['GENE'].str.contains('BRCA', na=False)])
    apoe_variants = len(df[df['GENE'].str.contains('APOE', na=False)])
    tp53_variants = len(df[df['GENE'].str.contains('TP53', na=False)])
    
    features = [
        high_risk, medium_risk, low_risk, pathogenic_count,
        avg_quality, brca_variants, apoe_variants, tp53_variants
    ]
    
    return features

def train_model():
    """Train disease prediction model"""
    # Generate realistic synthetic training data based on clinical patterns
    # In production, this would use de-identified patient genomic data with IRB approval
    np.random.seed(42)
    n_samples = 5000  # Increased for better model performance
    
    X = []
    y = []
    
    print("Generating training dataset based on clinical genomic patterns...")
    
    for i in range(n_samples):
        # Simulate realistic feature distributions based on genomic literature
        # Features represent variant counts and quality metrics from patient genomes
        
        high_risk = np.random.poisson(1.5)  # High-risk pathogenic variants are rare
        medium_risk = np.random.poisson(3)   # Medium-risk variants more common
        low_risk = np.random.poisson(15)     # Most variants are low-risk
        pathogenic = np.random.poisson(0.8)  # Pathogenic variants rare in general population
        quality = np.random.normal(35, 12)   # Sequencing quality scores
        
        # Cancer-related genes (BRCA1/2, TP53, etc.)
        brca = np.random.poisson(0.3)
        apoe = np.random.poisson(0.2)
        tp53 = np.random.poisson(0.15)
        
        features = [high_risk, medium_risk, low_risk, pathogenic, quality, brca, apoe, tp53]
        
        # Clinical risk calculation based on evidence-weighted scoring
        # Mimics ACMG pathogenicity criteria weighting
        risk_score = (
            high_risk * 4.0 +      # Strong evidence weight
            medium_risk * 2.0 +     # Moderate evidence weight  
            pathogenic * 5.0 +      # Very strong evidence weight
            brca * 3.5 +            # Known cancer susceptibility
            tp53 * 4.0 +            # Guardian of genome
            apoe * 1.5              # Alzheimer's risk factor
        ) / 25.0
        
        # Add some biological noise and quality threshold
        if quality < 20:  # Low quality reduces confidence
            risk_score *= 0.7
        
        # Binary classification: High risk vs Low risk
        disease_risk = 1 if risk_score > 0.6 else 0
        
        X.append(features)
        y.append(disease_risk)
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"Generated {n_samples} training samples")
    print(f"Class distribution - High Risk: {np.sum(y)}, Low Risk: {len(y) - np.sum(y)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train XGBoost model
    model = xgb.XGBClassifier(random_state=42, eval_metric='logloss')
    model.fit(X_train, y_train)
    
    # Evaluate
    accuracy = model.score(X_test, y_test)
    print(f"Model accuracy: {accuracy:.3f}")
    
    # Save model
    os.makedirs('models', exist_ok=True)
    with open('models/model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("Model saved to models/model.pkl")
    return model

if __name__ == "__main__":
    train_model()