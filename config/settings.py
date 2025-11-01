from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    MONGODB_URL: str = "mongodb+srv://arpitsingh8124_db_user:WGqhXNnpOa7heAvu@cluster0.l3aagtb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    DATABASE_NAME: str = "HelixMed"
    
    # API
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Storage
    UPLOAD_DIR: str = "data/uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # ML Models
    MODEL_DIR: str = "models"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/genomeguard.log"
    
    class Config:
        env_file = ".env"

settings = Settings()