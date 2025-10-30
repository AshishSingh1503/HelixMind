from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.models.database import connect_to_mongo, close_mongo_connection
from backend.api import auth, analysis
from config.settings import settings
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stderr, level=settings.LOG_LEVEL)
logger.add(settings.LOG_FILE, rotation="10 MB", level=settings.LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting GenomeGuard API...")
    connect_to_mongo()
    yield
    # Shutdown
    logger.info("Shutting down GenomeGuard API...")
    close_mongo_connection()

app = FastAPI(
    title="GenomeGuard API",
    description="AI-Powered Genetic Disease Predictor Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(analysis.router)

@app.get("/")
async def root():
    return {"message": "GenomeGuard API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )