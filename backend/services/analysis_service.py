from datetime import datetime
import uuid
import os
from loguru import logger
from backend.models.database import get_database
from backend.models.schemas import AnalysisResult, AnalysisStatus

class AnalysisService:
    def __init__(self):
        self._db = get_database()
        # fallback in-memory store when DB is not available
        self._store = {}

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
                return doc
            except Exception as e:
                logger.warning(f"DB read failed: {e}")
        return self._store.get(analysis_id)

    async def get_user_analyses(self, user_id: str):
        if self._db:
            try:
                docs = list(self._db.analyses.find({"user_id": user_id}))
                return docs
            except Exception as e:
                logger.warning(f"DB read failed: {e}")
        # filter in-memory
        return [v for v in self._store.values() if v["user_id"] == user_id]

    def process_vcf(self, analysis_id: str, file_path: str):
        """Background processing stub: mark analysis as processing and then completed.
        Replace with real preprocessing/ML pipeline.
        """
        logger.info(f"Starting processing for {analysis_id} on file {file_path}")
        # Update DB or in-memory status
        try:
            if self._db:
                self._db.analyses.update_one({"_id": analysis_id}, {"$set": {"status": AnalysisStatus.PROCESSING.value}})
            elif analysis_id in self._store:
                self._store[analysis_id]["status"] = AnalysisStatus.PROCESSING.value

            # Here you would call the real processing functions, e.g. scripts/preprocess.py
            # For now, we'll simulate completion by updating the record
            if self._db:
                self._db.analyses.update_one({"_id": analysis_id}, {"$set": {"status": AnalysisStatus.COMPLETED.value, "completed_at": datetime.utcnow()}})
            elif analysis_id in self._store:
                self._store[analysis_id]["status"] = AnalysisStatus.COMPLETED.value
                self._store[analysis_id]["completed_at"] = datetime.utcnow()

            logger.info(f"Processing completed for {analysis_id}")
        except Exception as e:
            logger.error(f"Processing failed for {analysis_id}: {e}")
            try:
                if self._db:
                    self._db.analyses.update_one({"_id": analysis_id}, {"$set": {"status": AnalysisStatus.FAILED.value, "error_message": str(e)}})
                elif analysis_id in self._store:
                    self._store[analysis_id]["status"] = AnalysisStatus.FAILED.value
                    self._store[analysis_id]["error_message"] = str(e)
            except Exception:
                pass
