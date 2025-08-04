from app.config import settings
import requests

class TikaService:
    def __init__(self):
        self.base_url = settings.tika_url_with_auth.rstrip('/')

    async def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/version")
            return response.ok
        except Exception:
            return False
