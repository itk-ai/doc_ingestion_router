from fastapi import FastAPI, HTTPException
from app.config import settings
from app.services.tika import TikaService
from app.api.models import HealthResponse

app = FastAPI(
    title=settings.APP_NAME,
    description="A service to route document loading requests to appropriate Tika endpoints",
    version="1.0.0"
)

@app.get("/health", tags=["Health"], response_model=HealthResponse)
async def health_check():
    tika_service = TikaService()
    tika_available = await tika_service.is_available()

    if not tika_available:
        raise HTTPException(status_code=503, detail="Tika service is not available")

    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }
