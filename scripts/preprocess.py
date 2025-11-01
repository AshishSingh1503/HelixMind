import pandas as pd
import os
import sys
import re

def preprocess_vcf(input_file, output_file):
    """Preprocess VCF file and extract variant information (Windows-compatible, no pysam)"""
    variants = []
    
    try:
        with open(input_file, 'r') as f:
            for line in f:
                # Skip header lines
                if line.startswith('##'):
                    continue
                    
                # Process column header line
                if line.startswith('#CHROM'):
                    headers = line.strip().split('\t')
                    sample_columns = headers[9:] if len(headers) > 9 else []
                    continue
                
                # Process variant lines
                if line.strip():
                    fields = line.strip().split('\t')
                    
                    if len(fields) < 8:
                        continue
                    
                    # Parse standard VCF fields
                    chrom = fields[0].replace('chr', '')  # Normalize chromosome
                    pos = int(fields[1]) if fields[1].isdigit() else 0
                    ref = fields[3]
                    alt = fields[4].split(',')[0] if fields[4] != '.' else ''
                    
                    # Parse quality score
                    try:
                        qual = float(fields[5]) if fields[5] != '.' else None
                    except ValueError:
                        qual = None
                    
                    filter_val = fields[6] if fields[6] != '.' else 'PASS'
                    
                    # Extract genotype if sample data exists
                    genotype = None
                    if len(fields) > 9:
                        format_fields = fields[8].split(':')
                        sample_data = fields[9].split(':')
                        
                        if 'GT' in format_fields:
                            gt_index = format_fields.index('GT')
                            if gt_index < len(sample_data):
                                genotype = sample_data[gt_index].replace('|', '/')
                    
                    variant = {
                        'CHROM': chrom,
                        'POS': pos,
                        'REF': ref,
                        'ALT': alt,
                        'QUAL': qual,
                        'FILTER': filter_val,
                        'GT': genotype
                    }
                    
                    variants.append(variant)
        
        if not variants:
            print("Warning: No variants found in VCF file")
            return False
        
        # Convert to DataFrame and save
        df = pd.DataFrame(variants)
        df.to_csv(output_file, index=False)
        print(f"Processed {len(variants)} variants from {input_file}")
        
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        return False
    except Exception as e:
        print(f"Error processing VCF: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    input_dir = "data/raw"
    output_dir = "data/processed"
    
    os.makedirs(output_dir, exist_ok=True)
    
    for file in os.listdir(input_dir):
        if file.endswith('.vcf'):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file.replace('.vcf', '_processed.csv'))
            
            print(f"Processing {file}...")
            if preprocess_vcf(input_path, output_path):
                print(f"Saved to {output_path}")