import pytest
from app.config import Settings

@pytest.fixture
def test_settings():
    return Settings(
        TIKA_BASE_URL="http://test-tika-server",
        API_KEY="test-api-key",
        TIKA_USER="test-user",
        TIKA_PASSWORD="test-password"
    )
