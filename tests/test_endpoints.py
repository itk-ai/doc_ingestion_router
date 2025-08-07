import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
import requests

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_unauthorized():
    headers = {
        "Content-Type": "text/plain",
        "X-Filename": "test.txt"
    }
    response = client.put(
        "/api/v1/process",
        content=b"test content",
        headers=headers
    )
    assert response.status_code == 401
    assert "Authorization header is missing" in response.json()["detail"]

def test_invalid_token():
    headers = {
        "Authorization": "Bearer invalid_token",
        "Content-Type": "text/plain",
        "X-Filename": "test.txt"
    }
    response = client.put(
        "/api/v1/process",
        content=b"test content",
        headers=headers
    )
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]

def test_invalid_format():
    headers = {
        "Authorization": settings.API_KEY,
        "Content-Type": "text/plain",
        "X-Filename": "test.txt"
    }
    response = client.put(
        "/api/v1/process",
        content= b"test content",
        headers=headers
    )
    assert response.status_code == 401
    assert "Invalid authorization header format" in response.json()["detail"]

def test_process_document_raw_data():
    headers = {
        "Authorization": f"Bearer {settings.API_KEY}",
        "Content-Type": "text/plain",
        "X-Filename": "test.txt"
    }
    response = client.put(
        "/api/v1/process",
        headers=headers,
        content=b"test content"
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "page_content" in response.json()["content"]

def test_process_document_using_data_field():
    # This mimics how OWUI communicates with an endpoint in the ExternalDocumentLoader class
    headers = {
        "Authorization": f"Bearer {settings.API_KEY}",
        "Content-Type": "text/plain",
        "X-Filename": "test.txt"
    }
    response = client.put(
        "/api/v1/process",
        data=b"test content",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "page_content" in response.json()["content"]

def test_process_document_raw_data_no_filename():
    headers = {
        "Authorization": f"Bearer {settings.API_KEY}",
        "Content-Type": "text/plain"
    }
    response = client.put(
        "/api/v1/process",
        headers=headers,
        content=b"test content"
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_process_document_no_content():
    headers = {
        "Authorization": f"Bearer {settings.API_KEY}",
        "Content-Type": "text/plain"
    }
    response = client.put(
        "/api/v1/process",
        headers=headers,
        content=b""
    )
    assert response.status_code == 400
    assert "No content provided" in response.json()["detail"]

