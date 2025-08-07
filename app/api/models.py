from pydantic import BaseModel
from typing import Optional, Dict, Any

class HealthResponse(BaseModel):
    status: str
    service: str

class DocumentResponse(BaseModel):
    page_content: str
    metadata: Dict[str, Any]

class DocumentProcessingResponse(BaseModel):
    success: bool
    content: DocumentResponse

# Not used at this point
# TODO: Check if used by end of vibe coding
class TikaError(BaseModel):
    detail: str
    status_code: int
