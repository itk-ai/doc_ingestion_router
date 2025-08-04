from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlparse, urlunparse

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    APP_NAME: str = "Document Ingestion Router"

    API_KEY: str

    TIKA_BASE_URL: str
    TIKA_USER: str
    TIKA_PASSWORD: str

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

settings = Settings()