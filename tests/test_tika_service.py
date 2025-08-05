import pytest
from app.services.tika import TikaService
from unittest.mock import Mock, patch
from fastapi import HTTPException


@pytest.fixture
def tika_service():
    return TikaService()


def test_detect_mime_type_with_tika(tika_service):
    with patch('requests.put') as mock_put:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "application/pdf"
        mock_put.return_value = mock_response

        mime_type = tika_service._detect_mime_type(b"fake content", "test.pdf")
        assert mime_type == "application/pdf"


def test_detect_mime_type_fallback(tika_service):
    with patch('requests.put', side_effect=Exception("Connection error")):
        mime_type = tika_service._detect_mime_type(b"fake content", "test.pdf")
        assert mime_type == "application/pdf"


def test_choose_tika_endpoint(tika_service):
    assert tika_service._choose_tika_endpoint("application/pdf") == "tika/text"
    assert tika_service._choose_tika_endpoint("application/msword") == "tika"


@pytest.mark.asyncio
async def test_process_document_pdf(tika_service):
    with patch('requests.put') as mock_put:
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "X-TIKA:content": "Test content"
        }
        mock_put.return_value = mock_response

        text, metadata = await tika_service.process_document(
            b"fake pdf content",
            filename="test.pdf",
            provided_mime_type="application/pdf"
        )
        assert text == "Test content"


@pytest.mark.asyncio
async def test_process_document_error(tika_service):
    with patch('requests.put') as mock_put:
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_put.return_value = mock_response

        with pytest.raises(HTTPException) as exc_info:
            await tika_service.process_document(b"fake content")
        assert exc_info.value.status_code == 500
