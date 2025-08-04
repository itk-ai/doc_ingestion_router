from pydantic_settings import BaseSettings
from urllib.parse import urlparse, urlunparse

class Settings(BaseSettings):
    TIKA_BASE_URL: str
    API_KEY: str
    TIKA_USER: str
    TIKA_PASSWORD: str
    APP_NAME: str = "Document Ingestion Router"

    @property
    def tika_url_with_auth(self) -> str:
        """Constructs Tika URL with authentication credentials"""
        parsed = urlparse(self.TIKA_BASE_URL)
        netloc = f"{self.TIKA_USER}:{self.TIKA_PASSWORD}@{parsed.netloc}"
        return urlunparse((
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            parsed.fragment
        ))

    class Config:
        env_file = ".env"

settings = Settings()
