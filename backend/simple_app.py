from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI(title="GenomeGuard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Settings
SECRET_KEY = "genomeguard-secret-key-change-in-production-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
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
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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