from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TIKA_BASE_URL: str
    API_KEY: str
    APP_NAME: str = "Document Ingestion Router"

    class Config:
        env_file = ".env"

settings = Settings()
