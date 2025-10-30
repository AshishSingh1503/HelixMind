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
    # Generate synthetic training data (in real implementation, use clinical datasets)
    np.random.seed(42)
    n_samples = 1000
    
    X = []
    y = []
    
    for i in range(n_samples):
        # Simulate feature vectors
        high_risk = np.random.poisson(2)
        medium_risk = np.random.poisson(5)
        low_risk = np.random.poisson(20)
        pathogenic = np.random.poisson(1)
        quality = np.random.normal(40, 10)
        brca = np.random.poisson(0.5)
        apoe = np.random.poisson(0.3)
        tp53 = np.random.poisson(0.2)
        
        features = [high_risk, medium_risk, low_risk, pathogenic, quality, brca, apoe, tp53]
        
        # Simple risk calculation for synthetic labels
        risk_score = (high_risk * 3 + medium_risk * 2 + pathogenic * 4 + brca * 5) / 20
        disease_risk = 1 if risk_score > 0.5 else 0
        
        X.append(features)
        y.append(disease_risk)
    
    X = np.array(X)
    y = np.array(y)
    
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