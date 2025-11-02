from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
from jose import jwt
from backend.models.database import get_database
from backend.models.schemas import User, UserCreate
from config.settings import settings
import uuid

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        salt, password_hash = hashed_password.split(':')
        return hashlib.sha256((plain_password + salt).encode()).hexdigest() == password_hash
    except Exception:
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

# In-memory user storage for fallback when DB not available
_memory_users = {}

async def create_user(user_data: UserCreate) -> Optional[User]:
    """Create a new user"""
    db = get_database()
    
    # Check if user exists in database
    if db is not None:
        existing_user = db.users.find_one({
            "$or": [
                {"username": user_data.username},
                {"email": user_data.email}
            ]
        })
        if existing_user:
            print(f"User already exists in database: {user_data.username}")
            return None
    else:
        # Check in-memory storage
        for user_id, user in _memory_users.items():
            if user["username"] == user_data.username or user["email"] == user_data.email:
                print(f"User already exists in memory: {user_data.username}")
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
    
    # Insert into database or memory
    if db is not None:
        try:
            db.users.insert_one(user_doc)
            print(f"✓ User created in MongoDB: {user_data.username}")
        except Exception as e:
            print(f"Failed to create user in MongoDB: {e}")
            return None
    else:
        # Store in memory
        _memory_users[user_id] = user_doc
        print(f"✓ User created in memory: {user_data.username}")
    
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
    user_doc = None
    
    # Try database first
    if db is not None:
        try:
            user_doc = db.users.find_one({"username": username})
        except Exception as e:
            print(f"Database query failed: {e}")
    
    # Fall back to memory storage
    if user_doc is None:
        for user_id, user in _memory_users.items():
            if user["username"] == username:
                user_doc = user
                break
    
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

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    db = get_database()
    user_doc = None
    
    # Try database first
    if db is not None:
        try:
            user_doc = db.users.find_one({"username": username})
        except Exception as e:
            print(f"Database query failed: {e}")
    
    # Fall back to memory storage
    if user_doc is None:
        for user_id, user in _memory_users.items():
            if user["username"] == username:
                user_doc = user
                break
    
    if not user_doc:
        print(f"User not found: {username}")
        return None
    
    if not verify_password(password, user_doc["hashed_password"]):
        print(f"Invalid password for user: {username}")
        return None
    
    print(f"✓ User authenticated: {username}")
    return User(
        id=user_doc["_id"],
        username=user_doc["username"],
        email=user_doc["email"],
        full_name=user_doc.get("full_name"),
        created_at=user_doc["created_at"],
        is_active=user_doc.get("is_active", True)
    )