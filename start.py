#!/usr/bin/env python3
import subprocess
import sys
import time
import webbrowser
import os

def start_backend():
    print("Starting backend API...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "backend.simple_app:app", 
        "--host", "127.0.0.1", 
        "--port", "8000", 
        "--reload"
    ])

def start_web():
    print("Starting React web application...")
    return subprocess.Popen(["npm", "start"], cwd="web", shell=True)

def main():
    print("GenomeGuard - Starting Application")
    print("=" * 35)
    
    try:
        # Start backend
        backend = start_backend()
        time.sleep(3)
        
        # Start web
        web = start_web()
        time.sleep(5)
        
        print("\nApplication Started!")
        print("Backend API: http://localhost:8000")
        print("Web App: http://localhost:3000")
        print("API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop")
        
        # Open browser
        webbrowser.open("http://localhost:3000")
        
        # Wait
        backend.wait()
        
    except KeyboardInterrupt:
        print("\nStopping services...")
        backend.terminate()
        web.terminate()
        print("Services stopped")

if __name__ == "__main__":
    main()