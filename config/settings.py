from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database - These MUST be set in .env file
    MONGODB_URL: str
    DATABASE_NAME: str = "HelixMed"
    
    # API - SECRET_KEY MUST be set in .env file
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    SECRET_KEY: str
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
        case_sensitive = True

settings = Settings()
