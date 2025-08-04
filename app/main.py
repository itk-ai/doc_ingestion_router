from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="A service to route document loading requests to appropriate Tika endpoints",
    version="1.0.0"
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME
    }
