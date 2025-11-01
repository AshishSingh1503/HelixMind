from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import jwt
from backend.models.database import get_database
from backend.models.schemas import User, UserCreate
from config.settings import settings
from loguru import logger
import uuid

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def create_user(user_data: UserCreate) -> Optional[User]:
    """Create a new user"""
    db = get_database()
    
    # Check if user exists
    if db is not None:
        existing_user = db.users.find_one({
            "$or": [
                {"username": user_data.username},
                {"email": user_data.email}
            ]
        })
        if existing_user:
            return None
    
    # Create user document
    user_id = str(uuid.uuid4())
    user_doc = {
        "_id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hash_password(user_data.password),
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Insert into database
    if db is not None:
        try:
            db.users.insert_one(user_doc)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return None
    
    return User(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        created_at=user_doc["created_at"],
        is_active=True
    )

async def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username"""
    db = get_database()
    
    if db is None:
        return None
    
    try:
        user_doc = db.users.find_one({"username": username})
        if not user_doc:
            return None
        
        return User(
            id=user_doc["_id"],
            username=user_doc["username"],
            email=user_doc["email"],
            full_name=user_doc.get("full_name"),
            created_at=user_doc["created_at"],
            is_active=user_doc.get("is_active", True)
        )
    except Exception as e:
        logger.error(f"Failed to get user: {e}")
        return None

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    db = get_database()
    
    if db is None:
        return None
    
    try:
        user_doc = db.users.find_one({"username": username})
        if not user_doc:
            return None
        
        if not verify_password(password, user_doc["hashed_password"]):
            return None
        
        return User(
            id=user_doc["_id"],
            username=user_doc["username"],
            email=user_doc["email"],
            full_name=user_doc.get("full_name"),
            created_at=user_doc["created_at"],
            is_active=user_doc.get("is_active", True)
        )
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return None
