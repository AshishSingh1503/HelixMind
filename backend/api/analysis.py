from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from typing import List
import os
import shutil
from backend.models.schemas import User, AnalysisResult
from backend.services.analysis_service import AnalysisService
from backend.api.auth import get_current_user
from config.settings import settings
from loguru import logger

router = APIRouter(prefix="/analysis", tags=["analysis"])
analysis_service = AnalysisService()

@router.post("/upload", response_model=dict)
async def upload_vcf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload VCF file and start analysis"""
    
    # Validate file
    if not file.filename.endswith('.vcf'):
        raise HTTPException(status_code=400, detail="Only VCF files are allowed")

    # Save file while enforcing max size. FastAPI's UploadFile does not provide a
    # reliable `size` attribute, so we stream the upload and count bytes.
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{file.filename}")

    max_size = settings.MAX_FILE_SIZE
    bytes_written = 0

    try:
        # Read in chunks from the UploadFile (async) and write to disk.
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > max_size:
                    # Clean up partial file
                    buffer.close()
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
                    raise HTTPException(status_code=400, detail="File too large")
                buffer.write(chunk)
    except HTTPException:
        # Re-raise known HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        # Try to remove partial file if exists
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="File upload failed")
    finally:
        # Ensure the uploaded file is closed
        try:
            await file.close()
        except Exception:
            pass
    
    # Create analysis record
    analysis_id = await analysis_service.create_analysis(current_user.id, file.filename)
    
    # Start background processing
    background_tasks.add_task(analysis_service.process_vcf, analysis_id, file_path)
    
    return {
        "message": "File uploaded successfully",
        "analysis_id": analysis_id,
        "filename": file.filename
    }

@router.get("/results/{analysis_id}", response_model=AnalysisResult)
async def get_analysis_results(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get analysis results by ID"""
    
    analysis = await analysis_service.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return analysis

@router.get("/history", response_model=List[AnalysisResult])
async def get_analysis_history(
    current_user: User = Depends(get_current_user)
):
    """Get user's analysis history"""
    
    analyses = await analysis_service.get_user_analyses(current_user.id)
    return analyses

@router.delete("/results/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete analysis and associated files"""
    
    analysis = await analysis_service.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete from database
    analysis_service.db.analyses.delete_one({"_id": analysis_id})
    
    # Delete associated file
    file_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{analysis.vcf_file}")
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return {"message": "Analysis deleted successfully"}