from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models.database import connect_to_mongo, close_mongo_connection
from backend.api.auth import router as auth_router
from backend.api.analysis import router as analysis_router
from loguru import logger

# Create FastAPI app
app = FastAPI(
    title="HelixMind API",
    description="Genomic Disease Risk Analysis Platform",
    version="1.0.0"
)

# Ensure CORS is properly configured - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "HelixMind API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include routers
logger.info("Registering authentication router")
app.include_router(auth_router)

logger.info("Registering analysis router")
app.include_router(analysis_router)

# Database event handlers
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)