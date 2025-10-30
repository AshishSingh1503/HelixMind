import pandas as pd
import os

# Simplified annotation database (in real implementation, use ClinVar/dbSNP)
DISEASE_VARIANTS = {
    'BRCA1': {'chrom': '17', 'genes': ['BRCA1'], 'diseases': ['Breast Cancer', 'Ovarian Cancer']},
    'BRCA2': {'chrom': '13', 'genes': ['BRCA2'], 'diseases': ['Breast Cancer', 'Ovarian Cancer']},
    'APOE': {'chrom': '19', 'genes': ['APOE'], 'diseases': ['Alzheimer Disease']},
    'TP53': {'chrom': '17', 'genes': ['TP53'], 'diseases': ['Li-Fraumeni Syndrome']},
}

def annotate_variants(input_file, output_file):
    """Annotate variants with disease associations"""
    df = pd.read_csv(input_file)
    
    # Add annotation columns
    df['GENE'] = ''
    df['DISEASE_RISK'] = 'Low'
    df['PATHOGENICITY'] = 'Benign'
    df['CLINICAL_SIG'] = 'Unknown'
    
    for idx, row in df.iterrows():
        chrom = str(row['CHROM'])
        
        # Simple position-based annotation (simplified)
        for variant_name, info in DISEASE_VARIANTS.items():
            if chrom == info['chrom']:
                # In real implementation, check exact positions and alleles
                if row['QUAL'] and row['QUAL'] > 30:  # Quality filter
                    df.at[idx, 'GENE'] = info['genes'][0]
                    df.at[idx, 'DISEASE_RISK'] = 'High' if 'Cancer' in info['diseases'][0] else 'Medium'
                    df.at[idx, 'PATHOGENICITY'] = 'Pathogenic'
                    df.at[idx, 'CLINICAL_SIG'] = ', '.join(info['diseases'])
    
    df.to_csv(output_file, index=False)
    print(f"Annotated {len(df)} variants")
    return True

if __name__ == "__main__":
    processed_dir = "data/processed"
    
    for file in os.listdir(processed_dir):
        if file.endswith('_processed.csv'):
            input_path = os.path.join(processed_dir, file)
            output_path = os.path.join(processed_dir, file.replace('_processed.csv', '_annotated.csv'))
            
            print(f"Annotating {file}...")
            annotate_variants(input_path, output_path)
            print(f"Saved to {output_path}")