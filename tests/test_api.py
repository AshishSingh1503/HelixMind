import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "GenomeGuard API is running" in response.json()["message"]

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_login():
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/auth/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.fixture
def auth_headers():
    # Login and get token
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/auth/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_get_user_profile(auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_upload_vcf_unauthorized():
    files = {"file": ("test.vcf", "test content", "text/plain")}
    response = client.post("/analysis/upload", files=files)
    assert response.status_code == 401