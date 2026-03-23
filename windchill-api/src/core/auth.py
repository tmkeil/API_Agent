"""
Authentication dependencies for FastAPI.

Supports:
1. Session cookie (frontend users with per-user Windchill credentials)
2. X-API-Key header (machine-to-machine, service account)
3. Azure AD Bearer token (optional SSO)
"""

import hmac
import logging
from typing import Optional

from fastapi import HTTPException, Request

from src.core.config import settings
from src.core.session import SESSION_COOKIE, UserSession, session_store

logger = logging.getLogger(__name__)


async def require_auth(request: Request) -> None:
    """
    FastAPI dependency: accepts session cookie, API-Key, or Azure AD Bearer.
    """
    # 1. Session cookie
    token = request.cookies.get(SESSION_COOKIE)
    if token and session_store.get(token):
        return

    # 2. API key (constant-time comparison)
    api_key = request.headers.get("X-API-Key", "")
    if settings.API_KEY and api_key and hmac.compare_digest(api_key, settings.API_KEY):
        return

    # 3. Azure AD Bearer
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer ") and settings.AZURE_TENANT_ID:
        _validate_azure_token(auth_header[7:])
        return

    raise HTTPException(
        status_code=401,
        detail="Authentifizierung erforderlich: Session, X-API-Key oder Bearer Token.",
    )


# Module-level JWKS client cache — avoids re-fetching keys on every token validation
_jwks_clients: dict[str, "PyJWKClient"] = {}
_jwks_lock = __import__("threading").Lock()


def _get_jwks_client(tenant_id: str) -> "PyJWKClient":
    """Return a cached PyJWKClient for the given Azure tenant."""
    with _jwks_lock:
        if tenant_id not in _jwks_clients:
            from jwt import PyJWKClient
            jwks_url = (
                f"https://login.microsoftonline.com/"
                f"{tenant_id}/discovery/v2.0/keys"
            )
            _jwks_clients[tenant_id] = PyJWKClient(jwks_url)
        return _jwks_clients[tenant_id]


def _validate_azure_token(token: str) -> None:
    if not settings.AZURE_TENANT_ID or not settings.AZURE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Azure AD nicht konfiguriert")
    try:
        import jwt
    except ImportError:
        raise HTTPException(status_code=500, detail="PyJWT nicht installiert")

    try:
        jwks_client = _get_jwks_client(settings.AZURE_TENANT_ID)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=[settings.AZURE_CLIENT_ID, f"api://{settings.AZURE_CLIENT_ID}"],
            issuer=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}/v2.0",
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token ungültig: {e}")