"""
Gemeinsame FastAPI-Dependencies fuer alle Router.

Eliminiert die duplizierte _get_session / _get_client Logik,
die vorher identisch in parts.py, search.py und admin.py stand.
"""

from typing import Optional

from fastapi import Request

from src.adapters.wrs_client import WRSClient, get_service_client
from src.core.session import SESSION_COOKIE, UserSession, session_store


def get_session(request: Request) -> Optional[UserSession]:
    """UserSession aus dem Session-Cookie aufloesen (falls vorhanden)."""
    token = request.cookies.get(SESSION_COOKIE)
    return session_store.get(token)


def get_client(request: Request) -> WRSClient:
    """WRSClient aufloesen: Session-Cookie zuerst, dann Service-Account."""
    session = get_session(request)
    if session:
        return session.client
    return get_service_client()
