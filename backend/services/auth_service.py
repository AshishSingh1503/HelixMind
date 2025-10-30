from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from backend.models.database import get_database
from backend.models.schemas import User, UserCreate
from config.settings import settings
from loguru import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

async def create_user(user_data: UserCreate):
    db = get_database()
    
    # Check if user exists
    if db.users.find_one({"$or": [{"username": user_data.username}, {"email": user_data.email}]}):
        return None
    
    user_dict = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": get_password_hash(user_data.password),
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    result = db.users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    return User(**user_dict)

async def authenticate_user(username: str, password: str):
    db = get_database()
    user = db.users.find_one({"username": username})
    
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    
    user["_id"] = str(user["_id"])
    return User(**user)

async def get_user_by_username(username: str):
    db = get_database()
    user = db.users.find_one({"username": username})
    
    if user:
        user["_id"] = str(user["_id"])
        return User(**user)
    return None