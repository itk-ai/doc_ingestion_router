from pydantic import BaseModel
from typing import Optional, Dict, Any

class HealthResponse(BaseModel):
    status: str
    service: str

class DocumentResponse(BaseModel):
    page_content: str
    metadata: Dict[str, Any]
