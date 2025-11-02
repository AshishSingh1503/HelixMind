#!/usr/bin/env python3
"""Test script for minimal GenomeGuard deployment"""

import requests
import json
import time

def test_api():
    base_url = "http://localhost:8000"
    
    print("Testing GenomeGuard Minimal API...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test registration
    try:
        user_data = {
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
        response = requests.post(f"{base_url}/auth/register", json=user_data, timeout=5)
        if response.status_code == 200:
            print("✅ User registration passed")
            token = response.json()["access_token"]
        else:
            print(f"❌ User registration failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User registration failed: {e}")
        return False
    
    # Test login
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpass123"
        }
        response = requests.post(f"{base_url}/auth/token", json=login_data, timeout=5)
        if response.status_code == 200:
            print("✅ User login passed")
        else:
            print(f"❌ User login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User login failed: {e}")
        return False
    
    # Test protected endpoint
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/auth/me", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Protected endpoint passed")
            user_info = response.json()
            print(f"   User: {user_info['full_name']} ({user_info['email']})")
        else:
            print(f"❌ Protected endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Protected endpoint failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Minimal deployment is working correctly.")
    return True

if __name__ == "__main__":
    test_api()