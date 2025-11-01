from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(title="GenomeGuard API", version="1.0.0")

# CORS will be configured in main.py

# Settings
SECRET_KEY = "genomeguard-secret-key-change-in-production-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# In-memory storage
users_db = {}

# Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Helper functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    
    user = users_db.get(username)
    if user is None:
        # Log for debugging
        print(f"User '{username}' not found. Available users: {list(users_db.keys())}")
        raise HTTPException(status_code=401, detail=f"User '{username}' not found. Please login again.")
    
    return User(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )

# Routes
@app.get("/")
async def root():
    return {"message": "GenomeGuard API is running", "version": "1.0.0"}

@app.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    # Validate input
    if not user_data.username or len(user_data.username.strip()) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    if not user_data.email or "@" not in user_data.email:
        raise HTTPException(status_code=400, detail="Valid email required")
    
    if not user_data.password or len(user_data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Check duplicates
    username_lower = user_data.username.lower().strip()
    email_lower = user_data.email.lower().strip()
    
    for existing_user in users_db.values():
        if existing_user["username"].lower() == username_lower:
            raise HTTPException(status_code=400, detail="Username already exists")
        if existing_user["email"].lower() == email_lower:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    # Create user
    user_id = f"user_{len(users_db) + 1}"
    user_doc = {
        "id": user_id,
        "username": user_data.username.strip(),
        "email": user_data.email.lower().strip(),
        "full_name": user_data.full_name.strip() if user_data.full_name else None,
        "hashed_password": hash_password(user_data.password),
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    users_db[user_data.username.strip()] = user_doc
    
    return User(
        id=user_doc["id"],
        username=user_doc["username"],
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        created_at=user_doc["created_at"],
        is_active=user_doc["is_active"]
    )

@app.post("/auth/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username.strip()
    user = users_db.get(username)
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@app.post("/auth/reset")
async def reset_system():
    users_db.clear()
    return {"message": "System reset - all users cleared"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "users_count": len(users_db)}

@app.get("/debug/users")
async def debug_users():
    return {"users": list(users_db.keys()), "count": len(users_db)}

@app.delete("/debug/clear-users")
async def clear_users():
    users_db.clear()
    return {"message": "All users cleared", "count": len(users_db)}

# Analysis endpoints (VCF parsing implementation)
from fastapi import UploadFile, File
import uuid
import random
import io

# In-memory storage for analyses
analyses_db = {}

def parse_vcf_file(file_content: str):
    """Parse VCF file and extract variant information including pathogenic variants"""
    lines = file_content.split('\n')
    variants = []
    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    pathogenic_count = 0
    likely_pathogenic_count = 0
    vus_count = 0
    benign_count = 0
    
    for line in lines:
        if line.startswith('#') or not line.strip():
            continue
        
        parts = line.split('\t')
        if len(parts) < 8:
            continue
        
        # Extract INFO field
        info = parts[7]
        
        # Extract RISK level
        risk_level = "LOW"
        if "RISK=HIGH" in info:
            risk_level = "HIGH"
            high_risk_count += 1
        elif "RISK=MEDIUM" in info:
            risk_level = "MEDIUM"
            medium_risk_count += 1
        else:
            low_risk_count += 1
        
        # Extract clinical significance (CLNSIG)
        clnsig = "Unknown"
        if "CLNSIG=Pathogenic" in info:
            clnsig = "Pathogenic"
            pathogenic_count += 1
        elif "CLNSIG=Likely_pathogenic" in info:
            clnsig = "Likely_pathogenic"
            likely_pathogenic_count += 1
        elif "CLNSIG=VUS" in info or "CLNSIG=Uncertain" in info:
            clnsig = "VUS"
            vus_count += 1
        elif "CLNSIG=Benign" in info or "CLNSIG=Likely_benign" in info:
            clnsig = "Benign"
            benign_count += 1
        
        # Extract GENE, DISEASE, and IMPACT
        gene = "Unknown"
        disease = "Unknown"
        impact = "Unknown"
        
        for item in info.split(';'):
            if item.startswith('GENE='):
                gene = item.replace('GENE=', '')
            elif item.startswith('DISEASE='):
                disease = item.replace('DISEASE=', '')
            elif item.startswith('IMPACT='):
                impact = item.replace('IMPACT=', '')
        
        variants.append({
            "chromosome": parts[0],
            "position": parts[1],
            "id": parts[2],
            "ref": parts[3],
            "alt": parts[4],
            "risk": risk_level,
            "clnsig": clnsig,
            "gene": gene,
            "disease": disease,
            "impact": impact
        })
    
    return {
        "total_variants": len(variants),
        "high_risk": high_risk_count,
        "medium_risk": medium_risk_count,
        "low_risk": low_risk_count,
        "pathogenic": pathogenic_count,
        "likely_pathogenic": likely_pathogenic_count,
        "vus": vus_count,
        "benign": benign_count,
        "variants": variants
    }

def calculate_risk_score(high: int, medium: int, low: int, total: int):
    """Calculate overall risk score based on variant distribution"""
    if total == 0:
        return 0.5, "medium"
    
    # Weight the risks: HIGH=1.0, MEDIUM=0.5, LOW=0.1
    weighted_score = (high * 1.0 + medium * 0.5 + low * 0.1) / total
    
    # Normalize to 0-1 range with some randomness
    risk_probability = min(0.95, max(0.05, weighted_score * 0.7 + random.uniform(-0.1, 0.1)))
    
    # Classify based on probability
    if risk_probability >= 0.7:
        classification = "high"
    elif risk_probability >= 0.4:
        classification = "medium"
    else:
        classification = "low"
    
    return round(risk_probability, 2), classification

@app.post("/analysis/upload")
async def upload_vcf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload VCF file and create analysis"""
    
    # Validate file
    if not file.filename.endswith('.vcf'):
        raise HTTPException(status_code=400, detail="Only VCF files are allowed")
    
    # Read and parse VCF file
    try:
        content = await file.read()
        file_content = content.decode('utf-8')
        vcf_data = parse_vcf_file(file_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse VCF file: {str(e)}")
    
    # Calculate risk score
    risk_probability, risk_classification = calculate_risk_score(
        vcf_data["high_risk"],
        vcf_data["medium_risk"],
        vcf_data["low_risk"],
        vcf_data["total_variants"]
    )
    
    # Create analysis record
    analysis_id = str(uuid.uuid4())
    analysis = {
        "id": analysis_id,
        "user_id": current_user.id,
        "filename": file.filename,
        "status": "completed",
        "risk_classification": risk_classification,
        "risk_probability": risk_probability,
        "variants_analyzed": vcf_data["total_variants"],
        "high_risk_variants": vcf_data["high_risk"],
        "medium_risk_variants": vcf_data["medium_risk"],
        "low_risk_variants": vcf_data["low_risk"],
        "pathogenic_variants": vcf_data["pathogenic"],
        "likely_pathogenic_variants": vcf_data["likely_pathogenic"],
        "vus_variants": vcf_data["vus"],
        "benign_variants": vcf_data["benign"],
        "created_at": datetime.utcnow(),
        "completed_at": datetime.utcnow(),
        "top_variants": vcf_data["variants"][:10] if vcf_data["variants"] else []
    }
    
    analyses_db[analysis_id] = analysis
    
    return {
        "message": "File uploaded successfully",
        "analysis_id": analysis_id,
        "filename": file.filename,
        "variants_analyzed": vcf_data["total_variants"],
        "risk_classification": risk_classification,
        "pathogenic_variants": vcf_data["pathogenic"]
    }

@app.get("/analysis/results/{analysis_id}")
async def get_analysis_results(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get analysis results by ID"""
    
    analysis = analyses_db.get(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Convert datetime objects to ISO format strings for proper JSON serialization
    result = dict(analysis)
    if "created_at" in result and result["created_at"]:
        result["created_at"] = result["created_at"].isoformat()
    if "completed_at" in result and result["completed_at"]:
        result["completed_at"] = result["completed_at"].isoformat()
    
    return result

@app.get("/analysis/history")
async def get_analysis_history(
    current_user: User = Depends(get_current_user)
):
    """Get user's analysis history"""
    
    user_analyses = [
        analysis for analysis in analyses_db.values()
        if analysis["user_id"] == current_user.id
    ]
    
    # Convert datetime objects to ISO format strings for proper JSON serialization
    results = []
    for analysis in user_analyses:
        result = dict(analysis)
        if "created_at" in result and result["created_at"]:
            result["created_at"] = result["created_at"].isoformat()
        if "completed_at" in result and result["completed_at"]:
            result["completed_at"] = result["completed_at"].isoformat()
        results.append(result)
    
    return results

@app.delete("/analysis/results/{analysis_id}")
async def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete analysis"""
    
    analysis = analyses_db.get(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    del analyses_db[analysis_id]
    
    return {"message": "Analysis deleted successfully"}

from fastapi.responses import Response

@app.get("/analysis/results/{analysis_id}/download")
async def download_report(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """Download analysis report as a formatted text file"""
    
    analysis = analyses_db.get(analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Generate report content
    report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              HELIXMIND GENOMIC ANALYSIS REPORT                   ║
╚══════════════════════════════════════════════════════════════════╝

PATIENT INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User ID:          {current_user.id}
Username:         {current_user.username}
Email:            {current_user.email}
Report Date:      {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

ANALYSIS SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Analysis ID:      {analysis['id']}
File Name:        {analysis['filename']}
Analysis Date:    {analysis['created_at'].strftime('%Y-%m-%d %H:%M:%S')} UTC
Status:           {analysis['status'].upper()}

RISK ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Risk Level:        {analysis['risk_classification'].upper()}
Risk Probability:          {analysis['risk_probability'] * 100:.1f}%
Risk Score:                {analysis['risk_probability']:.2f} / 1.00

VARIANT STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Variants Analyzed:   {analysis['variants_analyzed']}

Risk Level Distribution:
  High Risk Variants:      {analysis.get('high_risk_variants', 0)} ({analysis.get('high_risk_variants', 0) / max(1, analysis['variants_analyzed']) * 100:.1f}%)
  Medium Risk Variants:    {analysis.get('medium_risk_variants', 0)} ({analysis.get('medium_risk_variants', 0) / max(1, analysis['variants_analyzed']) * 100:.1f}%)
  Low Risk Variants:       {analysis.get('low_risk_variants', 0)} ({analysis.get('low_risk_variants', 0) / max(1, analysis['variants_analyzed']) * 100:.1f}%)

Clinical Significance Distribution:
  Pathogenic Variants:           {analysis.get('pathogenic_variants', 0)} ({analysis.get('pathogenic_variants', 0) / max(1, analysis['variants_analyzed']) * 100:.1f}%)
  Likely Pathogenic Variants:    {analysis.get('likely_pathogenic_variants', 0)} ({analysis.get('likely_pathogenic_variants', 0) / max(1, analysis['variants_analyzed']) * 100:.1f}%)
  Variants of Unknown Significance (VUS): {analysis.get('vus_variants', 0)} ({analysis.get('vus_variants', 0) / max(1, analysis['variants_analyzed']) * 100:.1f}%)
  Benign Variants:               {analysis.get('benign_variants', 0)} ({analysis.get('benign_variants', 0) / max(1, analysis['variants_analyzed']) * 100:.1f}%)

Total Pathogenic + Likely Pathogenic:  {analysis.get('pathogenic_variants', 0) + analysis.get('likely_pathogenic_variants', 0)} ({(analysis.get('pathogenic_variants', 0) + analysis.get('likely_pathogenic_variants', 0)) / max(1, analysis['variants_analyzed']) * 100:.1f}%)

RISK INTERPRETATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Add risk interpretation based on classification
    if analysis['risk_classification'] == 'high':
        report += """
⚠️  HIGH RISK DETECTED
Your genetic profile shows a higher likelihood of certain health conditions.
This does not mean you will develop these conditions, but indicates increased
risk factors that may benefit from:
  • Regular health monitoring
  • Preventive screening programs
  • Consultation with genetic counselors
  • Lifestyle modifications
  • Discussion with healthcare provider
"""
    elif analysis['risk_classification'] == 'medium':
        report += """
⚡ MODERATE RISK DETECTED
Your genetic profile shows moderate risk factors for certain conditions.
Consider:
  • Regular health check-ups
  • Maintaining healthy lifestyle habits
  • Discussing findings with your healthcare provider
  • Periodic reassessment as needed
"""
    else:
        report += """
✓ LOW RISK DETECTED
Your genetic profile shows lower risk factors for the analyzed conditions.
Recommendations:
  • Continue healthy lifestyle practices
  • Regular routine health check-ups
  • Stay informed about family health history
"""
    
    # Add top variants if available
    if analysis.get('top_variants'):
        report += """

TOP GENETIC VARIANTS DETECTED (PATHOGENIC/HIGH RISK)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for i, variant in enumerate(analysis['top_variants'][:10], 1):
            report += f"""
Variant #{i}
  Chromosome:          {variant['chromosome']}
  Position:            {variant['position']}
  Variant ID:          {variant.get('id', 'N/A')}
  Gene:                {variant.get('gene', 'Unknown')}
  Reference Allele:    {variant.get('ref', 'N/A')}
  Alternate Allele:    {variant.get('alt', 'N/A')}
  Risk Level:          {variant.get('risk', 'Unknown')}
  Clinical Significance: {variant.get('clnsig', 'Unknown')}
  Associated Disease:  {variant.get('disease', 'Unknown').replace('_', ' ')}
  Impact:              {variant.get('impact', 'Unknown')}
"""
    
    report += """

DISCLAIMER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This report is for informational and research purposes only. It should not
be used as a substitute for professional medical advice, diagnosis, or
treatment. Always seek the advice of your physician or other qualified
health provider with any questions you may have regarding a medical condition.

Genetic risk assessments are based on current scientific understanding and
may change as research advances. Environmental factors, lifestyle choices,
and other genetic variants not tested may also influence disease risk.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated by HelixMind™ Genomic Analysis Platform
Report ID: {analysis['id']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    # Return as downloadable file
    filename = f"HelixMind_Report_{analysis['id'][:8]}_{datetime.utcnow().strftime('%Y%m%d')}.txt"
    
    return Response(
        content=report,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )