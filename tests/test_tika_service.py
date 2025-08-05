import pytest
from app.services.tika import TikaService
from fastapi import HTTPException
import json

# See https://unix.stackexchange.com/a/277967 for empty pdf content
empty_pdf_content = b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000052 00000 n \n0000000101 00000 n \ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n178\n%%EOF\n'
# See https://github.com/fschutt/printpdf/wiki/1.1.1-Hello-World-PDF for hello world pdf content
hello_world_pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Title (Hallo World!) >>\nendobj\n2 0 obj\n<< /Type /Catalog\n   /Pages 3 0 R\n>>\nendobj\n3 0 obj\n<< /Type /Pages\n   /MediaBox [0 0 595 842]\n   /Resources\n   << /Font << /F1 4 0 R >>\n      /ProcSet [/PDF /Text]\n   >>\n   /Kids [5 0 R]\n   /Count 1\n>>\nendobj\n4 0 obj\n<< /Type /Font\n   /Subtype /Type1\n   /BaseFont /Helvetica\n   /Encoding /WinAnsiEncoding\n>>\nendobj\n5 0 obj\n<< /Type /Page\n   /Parent 3 0 R\n   /Contents 6 0 R\n>>\nendobj\n6 0 obj\n<< /Length 41\n>>\nstream\n/F1 48 Tf\nBT\n72 746 Td\n(Hallo World!) Tj\nET\nendstream\nendobj\nxref\n0 7\n0000000000 65535 f \n0000000009 00000 n \n0000000050 00000 n \n0000000102 00000 n \n0000000268 00000 n \n0000000374 00000 n \n0000000443 00000 n \ntrailer\n<< /Size 7\n   /Info 1 0 R\n   /Root 2 0 R\n>>\nstartxref\n534\n%%EOF\n'

with open("tests/test_data/aarhusdk_example.pdf", "rb") as fp:
    aarhusdk_example_pdf_content = fp.read()

with open('tests/test_data/empty.docx','br') as fp:
    empty_docx_content = fp.read()

with open('tests/test_data/hello_world.docx','br') as fp:
    hello_world_docx_content = fp.read()

with open('tests/test_data/hello_world.doc','br') as fp:
    hello_world_doc_content = fp.read()

pdf_mime_type = "application/pdf"
docx_mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
doc_mime_type = "application/msword"

@pytest.fixture
def tika_service():
    return TikaService()

@pytest.mark.parametrize(
    "file_content, expected_mime",
    [
        (empty_pdf_content, pdf_mime_type),
        (hello_world_pdf_content, pdf_mime_type),
        (aarhusdk_example_pdf_content, pdf_mime_type),
        (empty_docx_content, docx_mime_type),
        (hello_world_docx_content, docx_mime_type),
        (hello_world_doc_content, doc_mime_type),
    ],
)
def test_detect_mime_type(tika_service, file_content, expected_mime):
    mime_type = tika_service._detect_mime_type(file_content)
    assert mime_type == expected_mime

@pytest.mark.parametrize(
    "file_name, expected_mime",
    [
        ('test.pdf', pdf_mime_type),
        ('test.docx', docx_mime_type),
        ('test.doc', doc_mime_type),
    ],
)
def test_detect_mime_type_fallback(tika_service, mocker, file_name, expected_mime):
    mocker.patch("magic.from_buffer", side_effect=Exception("Mock an error"))
    mime_type = tika_service._detect_mime_type(b"fake content", file_name)
    assert mime_type == expected_mime

def test_choose_tika_endpoint(tika_service):
    assert tika_service._choose_tika_endpoint("application/pdf") == "tika/text"
    assert tika_service._choose_tika_endpoint("application/msword") == "tika"


with open('tests/test_data/hello_world_pdf_tika_resp.json', 'r') as fp:
    hello_world_pdf_tika_resp = json.load(fp)
hello_world_pdf_processed_text = "Hallo World!\n\n\nHallo World!"

with open('tests/test_data/hello_world_docx_tika_resp.xml','r') as fp:
    hello_world_docx_tika_resp = fp.read()
hello_world_docx_processed_text = 'Hello world!'

with open('tests/test_data/hello_world_doc_tika_resp.xml','r') as fp:
    hello_world_doc_tika_resp = fp.read()
hello_world_doc_processed_text = 'Hello world!'

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "file_content, tika_response, tika_resp_type, expected_out",
    [
        (hello_world_pdf_content, hello_world_pdf_tika_resp, 'json', hello_world_pdf_processed_text),
        (hello_world_docx_content, hello_world_docx_tika_resp, 'text', hello_world_docx_processed_text),
        (hello_world_doc_content, hello_world_doc_tika_resp, 'text', hello_world_doc_processed_text),
    ],
)
async def test_process_document(tika_service, mocker, file_content, tika_response, tika_resp_type, expected_out):
    mock_response = mocker.MagicMock()
    if tika_resp_type == 'json':
        mock_response.json.return_value = tika_response
    else:
        mock_response.text = tika_response

    # Patch 'requests.put' to return the mock response
    mocker.patch("requests.put", return_value=mock_response)

    text, metadata = await tika_service.process_document(
        file_content
    )
    assert text == expected_out


@pytest.mark.asyncio
async def test_process_document_error(tika_service, mocker):
    mock_response = mocker.MagicMock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal server error"

    # Patch 'requests.put' to return the mock response
    mocker.patch("requests.put", return_value=mock_response)

    with pytest.raises(HTTPException) as exc_info:
        await tika_service.process_document(b"fake content")
    assert exc_info.value.status_code == 500
