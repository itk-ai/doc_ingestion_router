from app.config import settings
import requests
from typing import Dict, Any, Tuple
import mimetypes
import logging
from fastapi import HTTPException
from html2text import HTML2Text
import magic

logger = logging.getLogger(__name__)

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
            return mime_type
        except Exception as e:
            if filename is not None:
                print(f"Error detecting MIME type for {filename}: {str(e)}")
            else:
                print(f"Error detecting MIME type: {str(e)}")

        # Fallback to Python's mimetype detection
        if filename:
            guessed_type = mimetypes.guess_type(filename)[0]
            if guessed_type:
                return guessed_type

        return "application/octet-stream"

    def _choose_tika_endpoint(self, mime_type: str) -> str:
        """
        Choose appropriate Tika endpoint based on MIME type
        """
        # PDF documents should use the text endpoint
        if mime_type == "application/pdf":
            return "tika/text"
        # All other documents use the main tika endpoint for HTML output
        return "tika"

    async def process_document(
            self,
            file_content: bytes,
            filename: str = None,
            provided_mime_type: str = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Process document through appropriate Tika endpoint
        """
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
                text = metadata.get("X-TIKA:content", "").strip()
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
