#!/usr/bin/env python3
"""
GenomeGuard Service Starter
Starts both backend API and frontend dashboard
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    """Start FastAPI backend"""
    print("Starting GenomeGuard Backend API...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "backend.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000",
        "--reload"
    ])

def start_frontend():
    """Start Streamlit frontend"""
    print("Starting GenomeGuard Frontend Dashboard...")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        "app/dashboard.py",
        "--server.port", "8501"
    ])

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.server_info()
        print("MongoDB is running")
        return True
    except Exception:
        print("MongoDB is not running")
        print("Please start MongoDB or run: docker-compose up -d mongodb")
        return False

def main():
    print("GenomeGuard - Starting Services")
    print("=" * 50)
    
    # Check MongoDB
    if not check_mongodb():
        return
    
    # Create necessary directories
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(3)  # Wait for backend to start
        
        # Start frontend
        frontend_process = start_frontend()
        
        print("\n" + "=" * 50)
        print("GenomeGuard Services Started!")
        print("Backend API: http://localhost:8000")
        print("Frontend Dashboard: http://localhost:8501")
        print("API Docs: http://localhost:8000/docs")
        print("=" * 50)
        print("Press Ctrl+C to stop all services")
        
        # Wait for processes
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\nStopping services...")
            backend_process.terminate()
            frontend_process.terminate()
            
            # Wait for graceful shutdown
            backend_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
            
            print("Services stopped successfully")
    
    except Exception as e:
        print(f"Error starting services: {e}")

if __name__ == "__main__":
    main()