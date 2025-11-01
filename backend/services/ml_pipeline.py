"""
ML Pipeline Service
Orchestrates the complete genomic analysis workflow:
1. Preprocess VCF → 2. Annotate variants → 3. Predict disease risk
"""

import os
import sys
from pathlib import Path
from loguru import logger
from typing import Dict, Optional
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.preprocess import preprocess_vcf
from scripts.annotate import annotate_variants
from scripts.predict import predict_disease_risk, load_model


class MLPipeline:
    """Complete ML pipeline for genomic variant analysis"""
    
    def __init__(self):
        """Initialize pipeline with necessary directories"""
        self.base_dir = project_root
        self.upload_dir = self.base_dir / "data" / "uploads"
        self.processed_dir = self.base_dir / "data" / "processed"
        self.models_dir = self.base_dir / "models"
        
        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if model exists
        self.model_path = self.models_dir / "model.pkl"
        if not self.model_path.exists():
            logger.warning("Model file not found. Run scripts/train.py first!")
            self.model = None
        else:
            try:
                self.model = load_model()
                logger.info("ML model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                self.model = None
    
    def process_vcf_file(self, vcf_path: str, analysis_id: str) -> Dict:
        """
        Run complete pipeline on a VCF file
        
        Args:
            vcf_path: Path to uploaded VCF file
            analysis_id: Unique identifier for this analysis
            
        Returns:
            Dictionary with analysis results
        """
        results = {
            'analysis_id': analysis_id,
            'status': 'failed',
            'total_variants': 0,
            'high_risk_variants': 0,
            'medium_risk_variants': 0,
            'low_risk_variants': 0,
            'pathogenic_variants': 0,
            'risk_probability': 0.0,
            'risk_classification': 'Unknown',
            'variants': [],
            'error_message': None
        }
        
        try:
            logger.info(f"Starting pipeline for analysis {analysis_id}")
            logger.info(f"Input VCF: {vcf_path}")
            
            # Step 1: Preprocess VCF
            logger.info("Step 1/3: Preprocessing VCF file...")
            processed_file = self._preprocess_step(vcf_path, analysis_id)
            if not processed_file:
                results['error_message'] = "Failed to preprocess VCF file"
                return results
            
            # Step 2: Annotate variants
            logger.info("Step 2/3: Annotating variants with disease associations...")
            annotated_file = self._annotate_step(processed_file, analysis_id)
            if not annotated_file:
                results['error_message'] = "Failed to annotate variants"
                return results
            
            # Step 3: Predict disease risk
            logger.info("Step 3/3: Predicting disease risk using ML model...")
            prediction_results = self._predict_step(annotated_file, vcf_path)
            if not prediction_results:
                results['error_message'] = "Failed to generate risk prediction"
                return results
            
            # Combine results
            results.update(prediction_results)
            results['status'] = 'completed'
            
            logger.info(f"Pipeline completed successfully for {analysis_id}")
            logger.info(f"Total variants: {results['total_variants']}")
            logger.info(f"High risk: {results['high_risk_variants']}")
            logger.info(f"Risk classification: {results['risk_classification']}")
            
            return results
            
        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            results['error_message'] = error_msg
            return results
    
    def _preprocess_step(self, vcf_path: str, analysis_id: str) -> Optional[str]:
        """Step 1: Preprocess VCF to CSV"""
        try:
            base_name = Path(vcf_path).stem
            processed_file = self.processed_dir / f"{analysis_id}_processed.csv"
            
            success = preprocess_vcf(vcf_path, str(processed_file))
            
            if success and processed_file.exists():
                logger.info(f"✓ Preprocessing complete: {processed_file}")
                return str(processed_file)
            else:
                logger.error("Preprocessing failed")
                return None
                
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            return None
    
    def _annotate_step(self, processed_file: str, analysis_id: str) -> Optional[str]:
        """Step 2: Annotate variants with disease info"""
        try:
            annotated_file = self.processed_dir / f"{analysis_id}_annotated.csv"
            
            success = annotate_variants(processed_file, str(annotated_file))
            
            if success and annotated_file.exists():
                logger.info(f"✓ Annotation complete: {annotated_file}")
                return str(annotated_file)
            else:
                logger.error("Annotation failed")
                return None
                
        except Exception as e:
            logger.error(f"Annotation error: {e}")
            return None
    
    def _predict_step(self, annotated_file: str, original_vcf: str) -> Optional[Dict]:
        """Step 3: Predict disease risk"""
        try:
            # Use the prediction function from predict.py with explicit annotated file path
            report = predict_disease_risk(original_vcf, annotated_file)
            
            if report:
                # Convert report to our result format
                results = {
                    'total_variants': report['total_variants'],
                    'high_risk_variants': report['high_risk_variants'],
                    'pathogenic_variants': report['pathogenic_variants'],
                    'risk_probability': report['disease_risk_probability'],
                    'risk_classification': report['risk_classification'].lower().replace(' ', '_'),
                    
                    # Add more detailed breakdown
                    'medium_risk_variants': report.get('medium_risk_variants', 0),
                    'low_risk_variants': report.get('low_risk_variants', 0),
                }
                
                logger.info(f"✓ Prediction complete")
                return results
            else:
                logger.error("Prediction returned no results")
                return None
                
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def cleanup_intermediate_files(self, analysis_id: str):
        """Clean up intermediate processing files"""
        try:
            patterns = [
                f"{analysis_id}_processed.csv",
                f"{analysis_id}_annotated.csv"
            ]
            
            for pattern in patterns:
                file_path = self.processed_dir / pattern
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"Cleaned up: {file_path}")
                    
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")


# Test the pipeline
if __name__ == "__main__":
    logger.info("Testing ML Pipeline...")
    
    pipeline = MLPipeline()
    
    # Test with sample VCF if it exists
    sample_vcf = project_root / "data" / "raw" / "sample.vcf"
    
    if sample_vcf.exists():
        logger.info(f"Running pipeline on {sample_vcf}")
        results = pipeline.process_vcf_file(str(sample_vcf), "test_analysis")
        
        print("\n" + "=" * 60)
        print("PIPELINE TEST RESULTS")
        print("=" * 60)
        print(f"Status: {results['status']}")
        print(f"Total Variants: {results['total_variants']}")
        print(f"High Risk: {results['high_risk_variants']}")
        print(f"Pathogenic: {results['pathogenic_variants']}")
        print(f"Risk Probability: {results['risk_probability']:.3f}")
        print(f"Classification: {results['risk_classification']}")
        
        if results['error_message']:
            print(f"Error: {results['error_message']}")
        print("=" * 60)
    else:
        logger.warning(f"Sample VCF not found: {sample_vcf}")
        print("Please provide a VCF file to test the pipeline")
