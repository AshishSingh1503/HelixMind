from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models.database import connect_to_mongo, close_mongo_connection
from backend.simple_app import app

# Ensure CORS is properly configured - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Use the working simple app
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)