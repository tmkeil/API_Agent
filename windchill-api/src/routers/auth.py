"""Auth endpoints for the frontend: login, logout, session info, system list."""

import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.adapters.wrs_client import WRSClient, WRSError
from src.core.config import WINDCHILL_SYSTEMS, settings
from src.core.session import SESSION_COOKIE, session_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Validated login payload — replaces raw request.json()."""
    system: str
    username: str
    password: str


@router.get("/systems")
def list_systems():
    """Available Windchill systems for login."""
    return {
        "systems": [
            {"key": k, "label": k.upper(), "url": v}
            for k, v in WINDCHILL_SYSTEMS.items()
        ]
    }


@router.post("/login")
async def login(body: LoginRequest, request: Request):
    system_key = body.system.strip().lower()
    username = body.username.strip()
    password = body.password

    if not system_key or system_key not in WINDCHILL_SYSTEMS:
        raise HTTPException(status_code=400, detail="Ungültiges Zielsystem")
    if not username or not password:
        raise HTTPException(
            status_code=400, detail="Benutzername und Passwort erforderlich"
        )

    system_url = WINDCHILL_SYSTEMS[system_key]

    logger.info(
        "Login-Versuch: system=%s url=%s user=%s",
        system_key, system_url, username,
    )

    try:
        client = WRSClient(
            base_url=system_url,
            username=username,
            password=password,
            odata_version=settings.WRS_ODATA_VERSION,
            verify_tls=settings.WRS_VERIFY_TLS,
            timeout=settings.WRS_TIMEOUT_SECONDS,
        )
    except WRSError as e:
        logger.error("Login WRSError: %s (status=%s)", e, e.status_code)
        raise  # Global exception handler converts to HTTP response
    except Exception as e:
        logger.error("Login Exception: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail=f"Verbindungsfehler: {e}")

    session = session_store.create(
        system_key=system_key,
        system_url=system_url,
        username=username,
        client=client,
    )

    response = JSONResponse(
        {
            "ok": True,
            "system": system_key,
            "systemUrl": system_url,
            "username": username,
        }
    )
    response.set_cookie(
        SESSION_COOKIE,
        session.token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=settings.SESSION_TTL_SECONDS,
    )
    return response


@router.post("/logout")
def logout(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    session_store.delete(token)
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE)
    return response


@router.get("/me")
def me(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    session = session_store.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    return {
        "ok": True,
        "username": session.username,
        "system": session.system_key,
        "systemUrl": session.system_url,
    }