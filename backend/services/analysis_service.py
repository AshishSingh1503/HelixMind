import os
import pandas as pd
import pickle
from datetime import datetime
from typing import List
from backend.models.database import get_database
from backend.models.schemas import AnalysisResult, AnalysisStatus, Variant, RiskLevel
from config.settings import settings
from loguru import logger

class AnalysisService:
    def __init__(self):
        self.db = get_database()
        self.model = self._load_model()
    
    def _load_model(self):
        model_path = os.path.join(settings.MODEL_DIR, "model.pkl")
        try:
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            logger.warning("Model not found, will need to train first")
            return None
    
    async def create_analysis(self, user_id: str, vcf_filename: str) -> str:
        """Create new analysis record"""
        analysis_data = {
            "user_id": user_id,
            "vcf_file": vcf_filename,
            "status": AnalysisStatus.PENDING,
            "created_at": datetime.utcnow(),
            "total_variants": 0,
            "high_risk_variants": 0,
            "pathogenic_variants": 0,
            "risk_probability": 0.0,
            "risk_classification": RiskLevel.LOW,
            "variants": []
        }
        
        result = self.db.analyses.insert_one(analysis_data)
        return str(result.inserted_id)
    
    async def process_vcf(self, analysis_id: str, vcf_path: str):
        """Process VCF file and update analysis"""
        try:
            # Update status to processing
            self.db.analyses.update_one(
                {"_id": analysis_id},
                {"$set": {"status": AnalysisStatus.PROCESSING}}
            )
            
            # Process VCF (simplified version)
            variants = self._extract_variants(vcf_path)
            annotated_variants = self._annotate_variants(variants)
            
            # Calculate risk
            risk_data = self._calculate_risk(annotated_variants)
            
            # Update analysis with results
            update_data = {
                "status": AnalysisStatus.COMPLETED,
                "completed_at": datetime.utcnow(),
                "total_variants": len(annotated_variants),
                "high_risk_variants": risk_data["high_risk_count"],
                "pathogenic_variants": risk_data["pathogenic_count"],
                "risk_probability": risk_data["risk_probability"],
                "risk_classification": risk_data["risk_level"],
                "variants": [v.dict() for v in annotated_variants]
            }
            
            self.db.analyses.update_one(
                {"_id": analysis_id},
                {"$set": update_data}
            )
            
            logger.info(f"Analysis {analysis_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}")
            self.db.analyses.update_one(
                {"_id": analysis_id},
                {"$set": {
                    "status": AnalysisStatus.FAILED,
                    "error_message": str(e)
                }}
            )
    
    def _extract_variants(self, vcf_path: str) -> List[dict]:
        """Extract variants from VCF file"""
        variants = []
        
        try:
            with open(vcf_path, 'r') as f:
                for line in f:
                    if line.startswith('#'):
                        continue
                    
                    parts = line.strip().split('\t')
                    if len(parts) >= 5:
                        variants.append({
                            'chrom': parts[0],
                            'pos': int(parts[1]),
                            'ref': parts[3],
                            'alt': parts[4],
                            'qual': float(parts[5]) if parts[5] != '.' else None
                        })
        except Exception as e:
            logger.error(f"Error extracting variants: {e}")
        
        return variants
    
    def _annotate_variants(self, variants: List[dict]) -> List[Variant]:
        """Annotate variants with disease information"""
        annotated = []
        
        disease_genes = {
            '17': {'genes': ['BRCA1', 'TP53'], 'diseases': ['Breast Cancer', 'Li-Fraumeni']},
            '13': {'genes': ['BRCA2'], 'diseases': ['Breast Cancer']},
            '19': {'genes': ['APOE'], 'diseases': ['Alzheimer Disease']}
        }
        
        for variant in variants:
            chrom = str(variant['chrom'])
            gene_info = disease_genes.get(chrom, {})
            
            risk_level = RiskLevel.LOW
            pathogenicity = "Benign"
            clinical_sig = None
            gene = None
            
            if gene_info and variant.get('qual', 0) > 30:
                gene = gene_info['genes'][0]
                risk_level = RiskLevel.HIGH if 'Cancer' in gene_info['diseases'][0] else RiskLevel.MEDIUM
                pathogenicity = "Pathogenic"
                clinical_sig = ', '.join(gene_info['diseases'])
            
            annotated.append(Variant(
                chrom=variant['chrom'],
                pos=variant['pos'],
                ref=variant['ref'],
                alt=variant['alt'],
                qual=variant.get('qual'),
                gene=gene,
                disease_risk=risk_level,
                pathogenicity=pathogenicity,
                clinical_significance=clinical_sig
            ))
        
        return annotated
    
    def _calculate_risk(self, variants: List[Variant]) -> dict:
        """Calculate overall disease risk"""
        high_risk_count = sum(1 for v in variants if v.disease_risk == RiskLevel.HIGH)
        pathogenic_count = sum(1 for v in variants if v.pathogenicity == "Pathogenic")
        
        # Simple risk calculation
        risk_score = (high_risk_count * 0.3 + pathogenic_count * 0.4) / len(variants) if variants else 0
        
        if risk_score > 0.7:
            risk_level = RiskLevel.HIGH
        elif risk_score > 0.3:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return {
            "high_risk_count": high_risk_count,
            "pathogenic_count": pathogenic_count,
            "risk_probability": min(risk_score, 1.0),
            "risk_level": risk_level
        }
    
    async def get_analysis(self, analysis_id: str) -> AnalysisResult:
        """Get analysis by ID"""
        analysis = self.db.analyses.find_one({"_id": analysis_id})
        if analysis:
            analysis["_id"] = str(analysis["_id"])
            return AnalysisResult(**analysis)
        return None
    
    async def get_user_analyses(self, user_id: str) -> List[AnalysisResult]:
        """Get all analyses for a user"""
        analyses = []
        cursor = self.db.analyses.find({"user_id": user_id}).sort("created_at", -1)
        
        for analysis in cursor:
            analysis["_id"] = str(analysis["_id"])
            analyses.append(AnalysisResult(**analysis))
        
        return analyses