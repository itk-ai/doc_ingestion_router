from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

# Create the security scheme for Bearer tokens
bearer_scheme = HTTPBearer(auto_error=False)


def get_bearer_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
):
    """
    Validate the Bearer token from the Authorization header.

    Args:
        credentials: The Bearer token credentials extracted from the Authorization header

    Returns:
        The validated token if authentication is successful

    Raises:
        HTTPException: If authentication fails
    """
    if credentials is None:
        raise HTTPException(
            status_code=401, detail="Missing Authorization header with Bearer token"
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401, detail="Authorization header must use Bearer scheme"
        )

    if credentials.credentials != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")

    return credentials.credentials
