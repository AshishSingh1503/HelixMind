"""
Variant Annotation Service
Provides both local (fast, reliable) and API-based (comprehensive) annotation options
"""

import requests
from typing import Dict, List, Optional
from loguru import logger
import time

class VariantAnnotator:
    """
    Hybrid variant annotation system supporting both:
    1. Local database (fast, reliable, 50+ key disease genes)
    2. MyVariant.info API (comprehensive, real-time)
    """
    
    def __init__(self, use_api: bool = False):
        """
        Initialize annotator
        
        Args:
            use_api: If True, uses MyVariant.info API for real-time annotations
                    If False, uses local curated database (recommended for demos)
        """
        self.use_api = use_api
        self.api_base_url = "https://myvariant.info/v1"
        self.cache = {}  # Simple in-memory cache
        
    def annotate_variant(self, chrom: str, pos: int, ref: str, alt: str) -> Optional[Dict]:
        """
        Annotate a single variant
        
        Args:
            chrom: Chromosome (e.g., "17", "X")
            pos: Position
            ref: Reference allele
            alt: Alternate allele
            
        Returns:
            Dictionary with annotation data or None
        """
        if not self.use_api:
            logger.info("Using local annotation database (fast mode)")
            return None  # Fallback to local annotations in annotate.py
        
        # Build HGVS identifier for API query
        hgvs_id = f"chr{chrom}:g.{pos}{ref}>{alt}"
        
        # Check cache first
        if hgvs_id in self.cache:
            logger.debug(f"Cache hit for {hgvs_id}")
            return self.cache[hgvs_id]
        
        try:
            logger.info(f"Querying MyVariant.info API for {hgvs_id}")
            
            # Query MyVariant.info API
            url = f"{self.api_base_url}/variant/{hgvs_id}"
            params = {
                'fields': 'clinvar,dbsnp,cadd,dbnsfp.genename,dbnsfp.clinvar',
                'assembly': 'hg38'
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse relevant information
                annotation = self._parse_myvariant_response(data)
                
                # Cache the result
                self.cache[hgvs_id] = annotation
                
                # Rate limiting: be nice to the API
                time.sleep(0.1)
                
                return annotation
            else:
                logger.warning(f"API returned status {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("MyVariant.info API timeout")
            return None
        except Exception as e:
            logger.error(f"Error querying MyVariant.info: {e}")
            return None
    
    def _parse_myvariant_response(self, data: Dict) -> Dict:
        """Parse MyVariant.info API response"""
        annotation = {
            'gene': None,
            'clinical_significance': 'Unknown',
            'disease': [],
            'pathogenicity': 'Uncertain',
            'risk_level': 'Low'
        }
        
        # Extract ClinVar information
        if 'clinvar' in data:
            clinvar = data['clinvar']
            
            # Get clinical significance
            if 'rcv' in clinvar:
                rcv = clinvar['rcv'] if isinstance(clinvar['rcv'], list) else [clinvar['rcv']]
                for record in rcv:
                    if 'clinical_significance' in record:
                        sig = record['clinical_significance']
                        annotation['clinical_significance'] = sig
                        
                        # Map clinical significance to pathogenicity
                        if 'pathogenic' in sig.lower():
                            annotation['pathogenicity'] = 'Pathogenic'
                            annotation['risk_level'] = 'High'
                        elif 'likely pathogenic' in sig.lower():
                            annotation['pathogenicity'] = 'Likely Pathogenic'
                            annotation['risk_level'] = 'Medium'
                        elif 'benign' in sig.lower():
                            annotation['pathogenicity'] = 'Benign'
                            annotation['risk_level'] = 'Low'
                    
                    # Get associated diseases
                    if 'conditions' in record:
                        conditions = record['conditions']
                        if isinstance(conditions, list):
                            annotation['disease'].extend(conditions)
                        else:
                            annotation['disease'].append(conditions)
        
        # Extract gene information
        if 'dbnsfp' in data and 'genename' in data['dbnsfp']:
            annotation['gene'] = data['dbnsfp']['genename']
        
        # Extract dbSNP ID
        if 'dbsnp' in data:
            annotation['rsid'] = data['dbsnp'].get('rsid', None)
        
        return annotation
    
    def batch_annotate(self, variants: List[Dict]) -> List[Dict]:
        """
        Annotate multiple variants efficiently
        
        Args:
            variants: List of variant dictionaries with chrom, pos, ref, alt
            
        Returns:
            List of annotated variants
        """
        if not self.use_api:
            logger.info("Batch annotation using local database")
            return variants
        
        logger.info(f"Batch annotating {len(variants)} variants via API")
        
        annotated_variants = []
        for variant in variants:
            annotation = self.annotate_variant(
                variant['chrom'],
                variant['pos'],
                variant['ref'],
                variant['alt']
            )
            
            if annotation:
                variant.update(annotation)
            
            annotated_variants.append(variant)
        
        return annotated_variants


# Example usage and testing
if __name__ == "__main__":
    # Demo: Show both modes
    
    print("=" * 60)
    print("VARIANT ANNOTATION SERVICE - DEMO")
    print("=" * 60)
    
    # Test variant: BRCA1 pathogenic variant
    test_variant = {
        'chrom': '17',
        'pos': 43094464,
        'ref': 'A',
        'alt': 'C'
    }
    
    print("\n1. LOCAL MODE (Fast, Reliable):")
    print("-" * 60)
    local_annotator = VariantAnnotator(use_api=False)
    result = local_annotator.annotate_variant(**test_variant)
    print(f"Result: Uses local curated database (50+ disease genes)")
    
    print("\n2. API MODE (Comprehensive, Real-time):")
    print("-" * 60)
    print("⚠️  Requires internet connection")
    print("⚠️  Subject to API rate limits (60/min)")
    print("Example: Would query MyVariant.info for real ClinVar data")
    
    # Uncomment to actually test API (requires internet)
    # api_annotator = VariantAnnotator(use_api=True)
    # result = api_annotator.annotate_variant(**test_variant)
    # print(f"Result: {result}")
    
    print("\n" + "=" * 60)
    print("PRODUCTION RECOMMENDATION:")
    print("- Use LOCAL mode for demos and rapid processing")
    print("- Use API mode for production with caching layer")
    print("- Hybrid: Local first, API fallback for unknown variants")
    print("=" * 60)
