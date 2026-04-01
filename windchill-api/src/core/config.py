import json
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings

# Default Windchill systems — override via WINDCHILL_SYSTEMS_JSON env var
_DEFAULT_SYSTEMS_JSON = json.dumps({
    "prod": "https://plm-prod.neuhausen.balluff.net/Windchill",
    "test": "https://plm-test.neuhausen.balluff.net/Windchill",
    "dev": "https://plm-dev.neuhausen.balluff.net/Windchill",
})


class Settings(BaseSettings):
    # Windchill connection (service account for API-key endpoints)
    WRS_BASE_URL: str = "https://plm-prod.neuhausen.balluff.net/Windchill"
    WRS_ODATA_VERSION: str = "v6"
    WRS_USERNAME: Optional[str] = None
    WRS_PASSWORD: Optional[str] = None
    WRS_VERIFY_TLS: bool = True
    WRS_TIMEOUT_SECONDS: float = 30.0

    # Azure AD (optional)
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None

    # Cache
    CACHE_TTL_SECONDS: int = 60
    CACHE_MAX_SIZE: int = 1000

    # API protection (optional – disabled if empty)
    API_KEY: Optional[str] = None

    # Performance logging
    LOG_TIMING: bool = True

    # Session TTL for frontend users (seconds)
    SESSION_TTL_SECONDS: int = 3600

    # Cookie security (True for production behind TLS)
    COOKIE_SECURE: bool = False

    # CORS origins (comma-separated in .env)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Windchill system registry — override via env var (JSON string)
    WINDCHILL_SYSTEMS_JSON: str = _DEFAULT_SYSTEMS_JSON

    @field_validator("WRS_BASE_URL")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    class Config:
        env_file = ".env"


settings = Settings()

# Parse system registry from settings (JSON → dict)
WINDCHILL_SYSTEMS: dict[str, str] = json.loads(settings.WINDCHILL_SYSTEMS_JSON)
