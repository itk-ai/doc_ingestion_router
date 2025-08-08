from app.config import settings
import requests
from typing import Dict, Any, Tuple
import mimetypes
from loguru import logger
# TODO: Add logging of what is requested and where it is sent to
from fastapi import HTTPException
from html2text import HTML2Text
import magic

class TikaService:
    def __init__(self):
        self.base_url = settings.tika_url_with_auth.rstrip('/')

    async def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/version")
            return response.ok
        except Exception:
            return False

    # TODO: Instead of using this mime_type detection method, use the method used in
    #   the owui_ingestion_test using magic.from_buffer and the containers (apt install) libmagic1
    def _detect_mime_type(self, file_content: bytes, filename: str = None) -> str:
        """
        Determine MIME type using multiple methods.
        """
        try:
            # Use python-magic to get MIME type from file content
            mime_type = magic.from_buffer(file_content, mime=True)
            logger.info(f"Detected MIME using system magic type: {mime_type}")
            return mime_type
        except Exception as e:
            if filename is not None:
                print(f"Error detecting MIME type for {filename}: {str(e)}")
            else:
                print(f"Error detecting MIME type: {str(e)}")

        # Fallback to Python's mimetype detection
        if filename:
            guessed_type = mimetypes.guess_type(filename)[0]
            logger.info(f"Detected MIME using Python's mimetype: {guessed_type}")
            if guessed_type:
                return guessed_type

        logger.warning(f"Failed to detect MIME type using application/octet-stream as a fallback.")

        return "application/octet-stream"

    def _choose_tika_endpoint(self, mime_type: str) -> str:
        """
        Choose appropriate Tika endpoint based on MIME type
        """
        # All documents beside pdfs should use the main tika endpoint for HTML output
        endpoint = "tika"
        # PDF documents should use the text endpoint
        if mime_type == "application/pdf":
            endpoint = "tika/text"
        logger.info(f"Using Tika endpoint: {endpoint} for MIME type: {mime_type}")
        return endpoint

    async def process_document(
            self,
            file_content: bytes,
            filename: str = None,
            provided_mime_type: str = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process document through appropriate Tika endpoint
        """
        logger_msg = "Processing document"
        if provided_mime_type:
            logger_msg += f" of MIME type {provided_mime_type}"
        if filename:
            logger_msg += f" with name {filename}"
        else:
            content = file_content.decode('utf-8', 'ignore')
            content_len = len(content)
            content = content[:min(1024, content_len)]
            logger_msg += f" which content starts with:\n{content}"
        logger.info(logger_msg)
        try:
            # Use provided MIME type or detect it
            mime_type = provided_mime_type or self._detect_mime_type(file_content, filename)

            # Prepare headers
            headers = {"Content-Type": mime_type}
            if filename:
                headers["X-Filename"] = filename

            # Choose endpoint based on MIME type
            endpoint = self._choose_tika_endpoint(mime_type)

            # Send request to Tika
            response = requests.put(
                f"{self.base_url}/{endpoint}",
                data=file_content,
                headers=headers
            )

            if not response.ok:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Tika service error: {response.text}"
                )

            # Handle response based on endpoint
            if endpoint == "tika/text":
                # Plain text response
                metadata = response.json()
                text = metadata.pop("X-TIKA:content", "").strip()
                if not text:
                    text = "<No text content found>"
            else:
                # HTML response that needs to be converted to markdown
                h = HTML2Text()
                h.ignore_links = False
                text = h.handle(response.text).strip()
                metadata = {"Content-Type": mime_type}
                if filename:
                    metadata["X-Filename"] = filename

            return text, metadata

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing document: {str(e)}"
            )
