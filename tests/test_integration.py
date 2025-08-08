import os
import pytest
import requests
from pathlib import Path
import dotenv

dotenv.load_dotenv()
BASE_URL = "http://localhost:8000/api/v1"
API_KEY = os.getenv("API_KEY", "default_dev_key")
APP_NAME = os.getenv("APP_NAME", "Document Ingestion Router")
TEST_DATA_DIR = Path(__file__).parent / "test_data"

resp = requests.get("http://localhost:8000/health")

pytestmark = pytest.mark.skipif(
    (resp.status_code != 200 | resp.json()["service"] != APP_NAME),
    reason="The local service have not spun up.")

def process_document(file_path: Path) -> requests.Response:
    """Helper function to send document to processing endpoint"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-Filename": file_path.name
    }

    with open(file_path, "rb") as f:
        content = f.read()

    return requests.put(f"{BASE_URL}/process", content=content, headers=headers)

def test_process_pdf_document():
    """Test processing a PDF document"""
    pdf_file = TEST_DATA_DIR / "aarhusdk_example.pdf"
    response = process_document(pdf_file)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "content" in data
    assert "page_content" in data["content"]
    assert "metadata" in data["content"]
    assert data["content"]["metadata"]["Content-Type"].startswith("application/pdf")

    # Check that we actually got some text content
    assert len(data["content"]["page_content"]) > 0

def test_process_docx_document():
    """Test processing a DOCX document"""
    docx_file = TEST_DATA_DIR / "hello_world.docx"
    response = process_document(docx_file)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "content" in data
    assert "page_content" in data["content"]
    assert len(data["content"]["page_content"]) > 0


def test_invalid_api_key():
    """Test that invalid API key is rejected"""
    pdf_file = TEST_DATA_DIR / "sample.pdf"
    headers = {
        "Authorization": "Bearer invalid_key",
        "X-Filename": pdf_file.name
    }

    with open(pdf_file, "rb") as f:
        content = f.read()

    response = requests.put(f"{BASE_URL}/process", content=content, headers=headers)
    assert response.status_code == 401


def test_empty_document():
    """Test handling of empty document"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "text/plain",
        "X-Filename": "empty.txt"
    }

    response = requests.put(f"{BASE_URL}/process", content="", headers=headers)
    assert response.status_code == 400
    assert "No content provided" in response.json()["detail"]
