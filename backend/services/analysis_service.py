from datetime import datetime
import uuid
import os
from loguru import logger
from backend.models.database import get_database
from backend.models.schemas import AnalysisResult, AnalysisStatus
from backend.services.ml_pipeline import MLPipeline

class AnalysisService:
    def __init__(self):
        self._db = get_database()
        # fallback in-memory store when DB is not available
        self._store = {}
        # Initialize ML pipeline
        self.ml_pipeline = MLPipeline()

    async def create_analysis(self, user_id: str, filename: str) -> str:
        analysis_id = str(uuid.uuid4())
        now = datetime.utcnow()
        record = {
            "_id": analysis_id,
            "user_id": user_id,
            "vcf_file": filename,
            "status": AnalysisStatus.PENDING.value,
            "total_variants": 0,
            "high_risk_variants": 0,
            "pathogenic_variants": 0,
            "risk_probability": 0.0,
            "risk_classification": "low",
            "variants": [],
            "created_at": now,
            "completed_at": None,
            "error_message": None,
        }

        if self._db:
            try:
                self._db.analyses.insert_one(record)
            except Exception as e:
                logger.warning(f"Could not write analysis to DB: {e}")
                # still keep in memory
                self._store[analysis_id] = record
        else:
            self._store[analysis_id] = record

        return analysis_id

    async def get_analysis(self, analysis_id: str):
        if self._db:
            try:
                doc = self._db.analyses.find_one({"_id": analysis_id})
                if doc:
                    # Ensure id field is present for frontend compatibility
                    doc['id'] = doc.get('_id')
                return doc
            except Exception as e:
                logger.warning(f"DB read failed: {e}")
        return self._store.get(analysis_id)

    async def get_user_analyses(self, user_id: str):
        if self._db:
            try:
                docs = list(self._db.analyses.find({"user_id": user_id}))
                # Ensure id field is present for frontend compatibility
                for doc in docs:
                    doc['id'] = doc.get('_id')
                return docs
            except Exception as e:
                logger.warning(f"DB read failed: {e}")
        # filter in-memory
        return [v for v in self._store.values() if v["user_id"] == user_id]

    def process_vcf(self, analysis_id: str, file_path: str):
        """
        Process VCF file through complete ML pipeline
        1. Preprocess VCF
        2. Annotate variants
        3. Predict disease risk
        4. Update database with results
        """
        logger.info(f"Starting ML pipeline for analysis {analysis_id}")
        logger.info(f"Processing file: {file_path}")
        
        try:
            # Update status to PROCESSING
            self._update_status(analysis_id, AnalysisStatus.PROCESSING.value)
            
            # Run complete ML pipeline
            results = self.ml_pipeline.process_vcf_file(file_path, analysis_id)
            
            # Check if pipeline succeeded
            if results['status'] == 'completed':
                # Update database with actual results
                update_data = {
                    "status": AnalysisStatus.COMPLETED.value,
                    "completed_at": datetime.utcnow(),
                    "total_variants": results['total_variants'],
                    "high_risk_variants": results['high_risk_variants'],
                    "pathogenic_variants": results['pathogenic_variants'],
                    "risk_probability": results['risk_probability'],
                    "risk_classification": results['risk_classification'],
                    "error_message": None
                }
                
                # Add optional fields if available
                if 'medium_risk_variants' in results:
                    update_data['medium_risk_variants'] = results['medium_risk_variants']
                if 'low_risk_variants' in results:
                    update_data['low_risk_variants'] = results['low_risk_variants']
                
                self._update_analysis(analysis_id, update_data)
                
                logger.info(f"✓ Analysis {analysis_id} completed successfully")
                logger.info(f"  Total variants: {results['total_variants']}")
                logger.info(f"  High risk: {results['high_risk_variants']}")
                logger.info(f"  Risk: {results['risk_classification']} ({results['risk_probability']:.2%})")
                
            else:
                # Pipeline failed
                error_msg = results.get('error_message', 'Unknown pipeline error')
                logger.error(f"Pipeline failed for {analysis_id}: {error_msg}")
                
                self._update_analysis(analysis_id, {
                    "status": AnalysisStatus.FAILED.value,
                    "error_message": error_msg
                })
                
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            logger.error(f"Failed to process {analysis_id}: {error_msg}")
            
            import traceback
            logger.error(traceback.format_exc())
            
            # Update status to FAILED
            self._update_analysis(analysis_id, {
                "status": AnalysisStatus.FAILED.value,
                "error_message": error_msg
            })
    
    def _update_status(self, analysis_id: str, status: str):
        """Update analysis status"""
        try:
            if self._db:
                self._db.analyses.update_one(
                    {"_id": analysis_id},
                    {"$set": {"status": status}}
                )
            elif analysis_id in self._store:
                self._store[analysis_id]["status"] = status
        except Exception as e:
            logger.warning(f"Failed to update status: {e}")
    
    def _update_analysis(self, analysis_id: str, update_data: dict):
        """Update analysis record with results"""
        try:
            if self._db:
                self._db.analyses.update_one(
                    {"_id": analysis_id},
                    {"$set": update_data}
                )
            elif analysis_id in self._store:
                self._store[analysis_id].update(update_data)
        except Exception as e:
            logger.error(f"Failed to update analysis: {e}")
