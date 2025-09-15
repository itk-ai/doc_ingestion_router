from fastapi import APIRouter, Depends, Request, Header, HTTPException
from app.core.security import get_bearer_token
from app.services.tika import TikaService
from app.api.models import DocumentResponse

router = APIRouter()


@router.put(
    "/process",
    response_model=DocumentResponse,
    dependencies=[Depends(get_bearer_token, use_cache=False)],
    tags=["Document Processing"],
)
async def process_document(
    request: Request,
    content_type: str = Header(None),
    x_filename: str = Header(None, alias="X-Filename"),
) -> DocumentResponse:
    """
    Process a document using Tika service.
    Automatically detects MIME type if not provided.
    """
    tika_service = TikaService()

    # Get the raw content from the request body
    content = await request.body()

    if not content:
        raise HTTPException(
            status_code=400, detail="No content provided - request body is empty"
        )

    # Process document
    text, metadata = await tika_service.process_document(
        file_content=content, filename=x_filename, provided_mime_type=content_type
    )

    return DocumentResponse(page_content=text, metadata=metadata)
