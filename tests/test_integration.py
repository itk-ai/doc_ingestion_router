import os
import pytest
import requests
from pathlib import Path
import dotenv
from loguru import logger

dotenv.load_dotenv()
TEST_PORT = os.getenv("TEST_PORT", "8000")
BASE_URL = f"http://localhost:{TEST_PORT}/api/v1"
API_KEY = os.getenv("API_KEY", "default_test_key")
APP_NAME = os.getenv("APP_NAME", "Document Ingestion Router")
TEST_DATA_DIR = Path(__file__).parent / "test_data"

try:
    resp = requests.get(f"http://localhost:{TEST_PORT}/health")
    logger.info(f"Health check response: {resp.json()}")
except requests.exceptions.ConnectionError:
    pytest.skip("The local service have not spun up.", allow_module_level=True)

pytestmark = pytest.mark.skipif(
    ((resp.status_code != 200) or (resp.json()["service"] != APP_NAME)),
    reason="The local service have not spun up.")

def process_document(file_path: Path) -> requests.Response:
    """Helper function to send document to processing endpoint"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-Filename": file_path.name
    }

    with open(file_path, "rb") as f:
        content = f.read()

    return requests.put(f"{BASE_URL}/process", data=content, headers=headers)

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
    headers = {
        "Authorization": "Bearer invalid_key",
        "X-Filename": "empty.pdf"
    }
    # See https://unix.stackexchange.com/a/277967 for empty pdf content
    empty_pdf_content = b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000101 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n'

    response = requests.put(f"{BASE_URL}/process", data=empty_pdf_content, headers=headers)
    assert response.status_code == 401


def test_empty_document():
    """Test handling of empty document"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "text/plain",
        "X-Filename": "empty.txt"
    }

    response = requests.put(f"{BASE_URL}/process", data="", headers=headers)
    assert response.status_code == 400
    assert "No content provided" in response.json()["detail"]
