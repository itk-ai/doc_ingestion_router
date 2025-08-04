# This implement basic token security
# https://fastapi.tiangolo.com/reference/security/?h=apikeyheader#fastapi.security.APIKeyHeader--usage
# For more advance use maybe start out by looking to https://fastapi.tiangolo.com/tutorial/security/

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


async def validate_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing"
        )

    # Extract token from "Bearer <token>"
    if not api_key.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Must start with 'Bearer'"
        )

    token = api_key.replace("Bearer ", "")

    if token != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return token
