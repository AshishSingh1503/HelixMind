#!/usr/bin/env python3
"""
GenomeGuard Web Starter
Starts backend API, web frontend, and optionally Streamlit dashboard
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_backend():
    """Start FastAPI backend"""
    print("🚀 Starting GenomeGuard Backend API...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "backend.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000",
        "--reload"
    ])

def start_web():
    """Start React web frontend"""
    print("🌐 Starting GenomeGuard Web Frontend...")
    return subprocess.Popen([
        "npm", "start"
    ], cwd="web")

def start_streamlit():
    """Start Streamlit dashboard (optional)"""
    print("📊 Starting Streamlit Dashboard...")
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
        print("✅ MongoDB is running")
        return True
    except Exception:
        print("❌ MongoDB is not running")
        print("Please start MongoDB or run: docker-compose up -d mongodb")
        return False

def check_node():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js is not installed")
    print("Please install Node.js from https://nodejs.org/")
    return False

def install_web_deps():
    """Install web dependencies"""
    web_dir = Path("web")
    if not (web_dir / "node_modules").exists():
        print("📦 Installing web dependencies...")
        result = subprocess.run(["npm", "install"], cwd="web")
        if result.returncode != 0:
            print("❌ Failed to install web dependencies")
            return False
    return True

def main():
    print("🧬 GenomeGuard - Starting Full Stack Application")
    print("=" * 60)
    
    # Check prerequisites
    if not check_mongodb():
        return
    
    if not check_node():
        return
    
    if not install_web_deps():
        return
    
    # Create necessary directories
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(3)  # Wait for backend to start
        
        # Start web frontend
        web_process = start_web()
        time.sleep(3)  # Wait for web to start
        
        # Ask if user wants Streamlit dashboard too
        start_dash = input("Start Streamlit dashboard too? (y/N): ").lower().strip()
        streamlit_process = None
        if start_dash == 'y':
            streamlit_process = start_streamlit()
        
        print("\n" + "=" * 60)
        print("🎉 GenomeGuard Full Stack Started!")
        print("🌐 Web Frontend: http://localhost:3000")
        print("📡 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        if streamlit_process:
            print("📊 Streamlit Dashboard: http://localhost:8501")
        print("=" * 60)
        print("Press Ctrl+C to stop all services")
        
        # Wait for processes
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            backend_process.terminate()
            web_process.terminate()
            if streamlit_process:
                streamlit_process.terminate()
            
            # Wait for graceful shutdown
            backend_process.wait(timeout=5)
            web_process.wait(timeout=5)
            if streamlit_process:
                streamlit_process.wait(timeout=5)
            
            print("✅ Services stopped successfully")
    
    except Exception as e:
        print(f"❌ Error starting services: {e}")

if __name__ == "__main__":
    main()