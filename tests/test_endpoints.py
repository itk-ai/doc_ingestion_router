import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings


client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_protected_route_without_token():
    response = client.get("/protected")
    assert response.status_code == 401
    assert "Authorization header is missing" in response.json()["detail"]

def test_protected_route_invalid_token():
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]

def test_protected_route_valid_token():
    headers = {"Authorization": f"Bearer {settings.API_KEY}"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200

def test_protected_route_invalid_format():
    headers = {"Authorization": settings.API_KEY}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401
    assert "Invalid authorization header format" in response.json()["detail"]
