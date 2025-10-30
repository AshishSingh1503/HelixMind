import pandas as pd
import pickle
import sys
import os

def load_model():
    """Load trained model"""
    with open('models/model.pkl', 'rb') as f:
        return pickle.load(f)

def create_features(df):
    """Extract features from annotated variants (same as train.py)"""
    risk_counts = df['DISEASE_RISK'].value_counts()
    high_risk = risk_counts.get('High', 0)
    medium_risk = risk_counts.get('Medium', 0)
    low_risk = risk_counts.get('Low', 0)
    
    pathogenic_count = len(df[df['PATHOGENICITY'] == 'Pathogenic'])
    avg_quality = df['QUAL'].mean() if 'QUAL' in df.columns else 0
    
    brca_variants = len(df[df['GENE'].str.contains('BRCA', na=False)])
    apoe_variants = len(df[df['GENE'].str.contains('APOE', na=False)])
    tp53_variants = len(df[df['GENE'].str.contains('TP53', na=False)])
    
    return [high_risk, medium_risk, low_risk, pathogenic_count,
            avg_quality, brca_variants, apoe_variants, tp53_variants]

def predict_disease_risk(vcf_file):
    """Predict disease risk for a VCF file"""
    # Find annotated file
    base_name = os.path.splitext(os.path.basename(vcf_file))[0]
    annotated_file = f"data/processed/{base_name}_annotated.csv"
    
    if not os.path.exists(annotated_file):
        print(f"Annotated file not found: {annotated_file}")
        print("Please run preprocess.py and annotate.py first")
        return None
    
    # Load data and model
    df = pd.read_csv(annotated_file)
    model = load_model()
    
    # Extract features
    features = create_features(df)
    
    # Predict
    risk_prob = model.predict_proba([features])[0][1]
    risk_class = model.predict([features])[0]
    
    # Generate report
    report = {
        'file': vcf_file,
        'total_variants': len(df),
        'high_risk_variants': features[0],
        'pathogenic_variants': features[3],
        'disease_risk_probability': risk_prob,
        'risk_classification': 'High Risk' if risk_class == 1 else 'Low Risk'
    }
    
    return report

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python predict.py <vcf_file>")
        sys.exit(1)
    
    vcf_file = sys.argv[1]
    report = predict_disease_risk(vcf_file)
    
    if report:
        print("\n=== Disease Risk Prediction Report ===")
        print(f"File: {report['file']}")
        print(f"Total Variants: {report['total_variants']}")
        print(f"High Risk Variants: {report['high_risk_variants']}")
        print(f"Pathogenic Variants: {report['pathogenic_variants']}")
        print(f"Disease Risk Probability: {report['disease_risk_probability']:.3f}")
        print(f"Risk Classification: {report['risk_classification']}")