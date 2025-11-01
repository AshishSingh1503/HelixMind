import pandas as pd
import os

# Comprehensive disease variant database (simulated ClinVar/dbSNP annotations)
# Maps chromosome regions to known disease genes
DISEASE_VARIANTS = {
    # Chromosome 1
    'MTHFR': {'chrom': '1', 'pos_range': (11845780, 11867680), 'genes': ['MTHFR'], 'diseases': ['Homocystinuria', 'Cardiovascular Disease'], 'risk': 'Medium'},
    'MUTYH': {'chrom': '1', 'pos_range': (45794855, 45806148), 'genes': ['MUTYH'], 'diseases': ['Colorectal Cancer'], 'risk': 'High'},
    'MPZ': {'chrom': '1', 'pos_range': (161222797, 161229300), 'genes': ['MPZ'], 'diseases': ['Charcot-Marie-Tooth Disease'], 'risk': 'High'},
    
    # Chromosome 2
    'MSH2': {'chrom': '2', 'pos_range': (47403067, 47710367), 'genes': ['MSH2'], 'diseases': ['Lynch Syndrome', 'Colorectal Cancer'], 'risk': 'High'},
    'MSH6': {'chrom': '2', 'pos_range': (47789652, 47810099), 'genes': ['MSH6'], 'diseases': ['Lynch Syndrome'], 'risk': 'High'},
    'APOB': {'chrom': '2', 'pos_range': (21224301, 21266945), 'genes': ['APOB'], 'diseases': ['Familial Hypercholesterolemia'], 'risk': 'Medium'},
    
    # Chromosome 3
    'MLH1': {'chrom': '3', 'pos_range': (37034840, 37092337), 'genes': ['MLH1'], 'diseases': ['Lynch Syndrome', 'Colorectal Cancer'], 'risk': 'High'},
    'VHL': {'chrom': '3', 'pos_range': (10183318, 10195354), 'genes': ['VHL'], 'diseases': ['Von Hippel-Lindau Syndrome'], 'risk': 'High'},
    'FANCD2': {'chrom': '3', 'pos_range': (10051871, 10143872), 'genes': ['FANCD2'], 'diseases': ['Fanconi Anemia'], 'risk': 'High'},
    
    # Chromosome 4
    'FGFR3': {'chrom': '4', 'pos_range': (1793306, 1808872), 'genes': ['FGFR3'], 'diseases': ['Achondroplasia', 'Bladder Cancer'], 'risk': 'Medium'},
    'HTT': {'chrom': '4', 'pos_range': (3074876, 3243960), 'genes': ['HTT'], 'diseases': ['Huntington Disease'], 'risk': 'High'},
    
    # Chromosome 5
    'APC': {'chrom': '5', 'pos_range': (112707498, 112846239), 'genes': ['APC'], 'diseases': ['Familial Adenomatous Polyposis', 'Colorectal Cancer'], 'risk': 'High'},
    'MSH3': {'chrom': '5', 'pos_range': (79950416, 80174502), 'genes': ['MSH3'], 'diseases': ['Colorectal Cancer'], 'risk': 'Medium'},
    
    # Chromosome 6
    'HFE': {'chrom': '6', 'pos_range': (26087509, 26098343), 'genes': ['HFE'], 'diseases': ['Hemochromatosis'], 'risk': 'Medium'},
    'HLA-B': {'chrom': '6', 'pos_range': (31321649, 31324989), 'genes': ['HLA-B'], 'diseases': ['Autoimmune Disorders'], 'risk': 'Low'},
    
    # Chromosome 7
    'CFTR': {'chrom': '7', 'pos_range': (117480025, 117668665), 'genes': ['CFTR'], 'diseases': ['Cystic Fibrosis'], 'risk': 'High'},
    'BRAF': {'chrom': '7', 'pos_range': (140719327, 140924929), 'genes': ['BRAF'], 'diseases': ['Melanoma', 'Colorectal Cancer'], 'risk': 'High'},
    'MET': {'chrom': '7', 'pos_range': (116672196, 116798386), 'genes': ['MET'], 'diseases': ['Papillary Renal Carcinoma'], 'risk': 'Medium'},
    
    # Chromosome 8
    'MYC': {'chrom': '8', 'pos_range': (127735434, 127742951), 'genes': ['MYC'], 'diseases': ['Burkitt Lymphoma', 'Various Cancers'], 'risk': 'High'},
    
    # Chromosome 9
    'CDKN2A': {'chrom': '9', 'pos_range': (21967751, 21995301), 'genes': ['CDKN2A'], 'diseases': ['Melanoma', 'Pancreatic Cancer'], 'risk': 'High'},
    
    # Chromosome 10
    'PTEN': {'chrom': '10', 'pos_range': (87863113, 87971930), 'genes': ['PTEN'], 'diseases': ['Cowden Syndrome', 'Various Cancers'], 'risk': 'High'},
    'RET': {'chrom': '10', 'pos_range': (43077027, 43130531), 'genes': ['RET'], 'diseases': ['Thyroid Cancer', 'MEN2'], 'risk': 'High'},
    
    # Chromosome 11
    'HBB': {'chrom': '11', 'pos_range': (5225463, 5229395), 'genes': ['HBB'], 'diseases': ['Sickle Cell Disease', 'Thalassemia'], 'risk': 'High'},
    'ATM': {'chrom': '11', 'pos_range': (108222484, 108369102), 'genes': ['ATM'], 'diseases': ['Ataxia-Telangiectasia', 'Breast Cancer'], 'risk': 'High'},
    'MEN1': {'chrom': '11', 'pos_range': (64570985, 64578765), 'genes': ['MEN1'], 'diseases': ['Multiple Endocrine Neoplasia'], 'risk': 'High'},
    
    # Chromosome 12
    'KRAS': {'chrom': '12', 'pos_range': (25205246, 25250936), 'genes': ['KRAS'], 'diseases': ['Colorectal Cancer', 'Lung Cancer'], 'risk': 'High'},
    'VWF': {'chrom': '12', 'pos_range': (6093537, 6273740), 'genes': ['VWF'], 'diseases': ['Von Willebrand Disease'], 'risk': 'Medium'},
    
    # Chromosome 13
    'BRCA2': {'chrom': '13', 'pos_range': (32315086, 32400266), 'genes': ['BRCA2'], 'diseases': ['Breast Cancer', 'Ovarian Cancer', 'Prostate Cancer'], 'risk': 'High'},
    'RB1': {'chrom': '13', 'pos_range': (48303751, 48481890), 'genes': ['RB1'], 'diseases': ['Retinoblastoma'], 'risk': 'High'},
    
    # Chromosome 14
    'SERPINA1': {'chrom': '14', 'pos_range': (94376868, 94390692), 'genes': ['SERPINA1'], 'diseases': ['Alpha-1 Antitrypsin Deficiency'], 'risk': 'Medium'},
    
    # Chromosome 15
    'FBN1': {'chrom': '15', 'pos_range': (48408313, 48645709), 'genes': ['FBN1'], 'diseases': ['Marfan Syndrome'], 'risk': 'High'},
    
    # Chromosome 16
    'PKD1': {'chrom': '16', 'pos_range': (2088708, 2135898), 'genes': ['PKD1'], 'diseases': ['Polycystic Kidney Disease'], 'risk': 'High'},
    'CDH1': {'chrom': '16', 'pos_range': (68737289, 68835630), 'genes': ['CDH1'], 'diseases': ['Gastric Cancer', 'Breast Cancer'], 'risk': 'High'},
    
    # Chromosome 17
    'BRCA1': {'chrom': '17', 'pos_range': (43044295, 43125483), 'genes': ['BRCA1'], 'diseases': ['Breast Cancer', 'Ovarian Cancer'], 'risk': 'High'},
    'TP53': {'chrom': '17', 'pos_range': (7661779, 7687550), 'genes': ['TP53'], 'diseases': ['Li-Fraumeni Syndrome', 'Various Cancers'], 'risk': 'High'},
    'NF1': {'chrom': '17', 'pos_range': (31094927, 31377677), 'genes': ['NF1'], 'diseases': ['Neurofibromatosis Type 1'], 'risk': 'High'},
    'RARA': {'chrom': '17', 'pos_range': (40309152, 40357643), 'genes': ['RARA'], 'diseases': ['Acute Promyelocytic Leukemia'], 'risk': 'High'},
    
    # Chromosome 18
    'SMAD4': {'chrom': '18', 'pos_range': (51028394, 51085045), 'genes': ['SMAD4'], 'diseases': ['Juvenile Polyposis', 'Pancreatic Cancer'], 'risk': 'High'},
    
    # Chromosome 19
    'APOE': {'chrom': '19', 'pos_range': (44905791, 44909395), 'genes': ['APOE'], 'diseases': ['Alzheimer Disease', 'Cardiovascular Disease'], 'risk': 'Medium'},
    'LDLR': {'chrom': '19', 'pos_range': (11200038, 11244505), 'genes': ['LDLR'], 'diseases': ['Familial Hypercholesterolemia'], 'risk': 'High'},
    'NOTCH3': {'chrom': '19', 'pos_range': (15159041, 15311763), 'genes': ['NOTCH3'], 'diseases': ['CADASIL'], 'risk': 'Medium'},
    
    # Chromosome 20
    'JAK2': {'chrom': '20', 'pos_range': (31003499, 31084094), 'genes': ['JAK2'], 'diseases': ['Myeloproliferative Disorders'], 'risk': 'Medium'},
    
    # Chromosome 21
    'APP': {'chrom': '21', 'pos_range': (25880550, 26171128), 'genes': ['APP'], 'diseases': ['Alzheimer Disease'], 'risk': 'Medium'},
    
    # Chromosome 22
    'NF2': {'chrom': '22', 'pos_range': (29999545, 30094589), 'genes': ['NF2'], 'diseases': ['Neurofibromatosis Type 2'], 'risk': 'High'},
    
    # Chromosome X
    'DMD': {'chrom': 'X', 'pos_range': (31119220, 33339388), 'genes': ['DMD'], 'diseases': ['Duchenne Muscular Dystrophy'], 'risk': 'High'},
    'F8': {'chrom': 'X', 'pos_range': (154064063, 154250998), 'genes': ['F8'], 'diseases': ['Hemophilia A'], 'risk': 'High'},
    'F9': {'chrom': 'X', 'pos_range': (139530557, 139563458), 'genes': ['F9'], 'diseases': ['Hemophilia B'], 'risk': 'High'},
    'FMR1': {'chrom': 'X', 'pos_range': (147910000, 147950000), 'genes': ['FMR1'], 'diseases': ['Fragile X Syndrome'], 'risk': 'High'},
}

def annotate_variants(input_file, output_file):
    """Annotate variants with disease associations"""
    df = pd.read_csv(input_file)
    
    # Add annotation columns
    df['GENE'] = ''
    df['DISEASE_RISK'] = 'Low'
    df['PATHOGENICITY'] = 'Benign'
    df['CLINICAL_SIG'] = 'Unknown'
    
    annotated_count = 0
    
    for idx, row in df.iterrows():
        chrom = str(row['CHROM']).replace('chr', '')  # Normalize chromosome format
        pos = int(row['POS']) if 'POS' in row and pd.notna(row['POS']) else 0
        
        # Position-based annotation with quality filter
        if row.get('QUAL') and row['QUAL'] > 20:  # Quality threshold
            for variant_name, info in DISEASE_VARIANTS.items():
                if chrom == info['chrom']:
                    # Check if position falls within gene range
                    if 'pos_range' in info:
                        start, end = info['pos_range']
                        if start <= pos <= end:
                            df.at[idx, 'GENE'] = info['genes'][0]
                            df.at[idx, 'DISEASE_RISK'] = info['risk']
                            df.at[idx, 'PATHOGENICITY'] = 'Pathogenic' if info['risk'] == 'High' else 'Likely Pathogenic'
                            df.at[idx, 'CLINICAL_SIG'] = ', '.join(info['diseases'])
                            annotated_count += 1
                            break
                    else:
                        # Fallback for variants without position range (chromosome match only)
                        df.at[idx, 'GENE'] = info['genes'][0]
                        df.at[idx, 'DISEASE_RISK'] = info.get('risk', 'Medium')
                        df.at[idx, 'PATHOGENICITY'] = 'Likely Pathogenic'
                        df.at[idx, 'CLINICAL_SIG'] = ', '.join(info['diseases'])
                        annotated_count += 1
                        break
    
    df.to_csv(output_file, index=False)
    print(f"Annotated {len(df)} variants ({annotated_count} matched disease genes)")
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