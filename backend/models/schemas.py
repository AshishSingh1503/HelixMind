from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool = True
    
    class Config:
        populate_by_name = True

class VCFUpload(BaseModel):
    filename: str
    file_size: int
    upload_date: datetime
    user_id: str

class Variant(BaseModel):
    chrom: str
    pos: int
    ref: str
    alt: str
    qual: Optional[float]
    gene: Optional[str]
    disease_risk: RiskLevel
    pathogenicity: str
    clinical_significance: Optional[str]

class AnalysisResult(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: str
    vcf_file: str
    status: AnalysisStatus
    total_variants: int
    high_risk_variants: int
    pathogenic_variants: int
    risk_probability: float
    risk_classification: RiskLevel
    variants: List[Variant]
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class PredictionRequest(BaseModel):
    vcf_file_id: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None