import pandas as pd
import pysam
import os
import sys

def preprocess_vcf(input_file, output_file):
    """Preprocess VCF file and extract variant information"""
    variants = []
    
    try:
        vcf = pysam.VariantFile(input_file)
        
        for record in vcf:
            variant = {
                'CHROM': record.chrom,
                'POS': record.pos,
                'REF': record.ref,
                'ALT': str(record.alts[0]) if record.alts else '',
                'QUAL': record.qual,
                'FILTER': str(record.filter),
                'GT': None
            }
            
            # Extract genotype if available
            for sample in record.samples:
                gt = record.samples[sample]['GT']
                if gt:
                    variant['GT'] = '/'.join(str(x) if x is not None else '.' for x in gt)
                break
            
            variants.append(variant)
        
        vcf.close()
        
        # Convert to DataFrame and save
        df = pd.DataFrame(variants)
        df.to_csv(output_file, index=False)
        print(f"Processed {len(variants)} variants")
        
    except Exception as e:
        print(f"Error processing VCF: {e}")
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