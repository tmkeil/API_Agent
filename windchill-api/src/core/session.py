"""
Server-side session management for frontend users.
Each session holds a per-user WRSClient connected to the selected Windchill system,
plus per-session caches and an API activity log (deque).
"""

import secrets
import threading
import time
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from typing import Any

from src.adapters.wrs_client import WRSClient
from src.core.config import settings

SESSION_COOKIE = "wt_session"

# Maximum entries per session-level cache dict (LRU eviction)
_SESSION_CACHE_MAX = 500


class BoundedLRUDict(OrderedDict):
    """OrderedDict with a max size — evicts oldest entry on overflow."""

    def __init__(self, maxsize: int = _SESSION_CACHE_MAX):
        super().__init__()
        self._maxsize = maxsize

    def __setitem__(self, key: Any, value: Any) -> None:
        if key in self:
            self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self._maxsize:
            self.popitem(last=False)


@dataclass
class UserSession:
    token: str
    system_key: str
    system_url: str
    username: str
    client: WRSClient
    expires_at: float
    # Per-session caches — bounded LRU to prevent unbounded memory growth
    part_by_id: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    part_by_number: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    bom_children_by_part: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    documents_by_part: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    cad_documents_by_part: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    search_cache: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    api_logs: deque = field(default_factory=lambda: deque(maxlen=500))
    lock: threading.Lock = field(default_factory=threading.Lock)


def log_session_event(
    session: UserSession,
    method: str,
    url: str,
    status: int,
    duration_ms: int,
    source: str,
    note: str = "",
) -> None:
    """Append an API activity log entry to the session's log deque."""
    import datetime

    entry = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": source,
        "method": method,
        "url": url,
        "status": status,
        "durationMs": duration_ms,
        "note": note,
    }
    with session.lock:
        session.api_logs.appendleft(entry)


def instrument_client_requests(session: UserSession) -> None:
    """Attach httpx event hooks to the session's WRSClient for automatic
    API activity logging.

    Uses httpx's built-in ``event_hooks`` API instead of monkey-patching
    ``_raw_get``.  A *request* hook records the start time in
    ``request.extensions``; the *response* hook calculates the latency
    and writes an entry to ``session.api_logs``.
    """
    client = session.client
    if getattr(client, "_instrumented", False):
        return

    http_client = client._http  # underlying httpx.Client

    def _on_request(request):
        """Store start time so the response hook can compute latency."""
        request.extensions["_log_start"] = time.perf_counter()

    def _on_response(response):
        """Log the completed Windchill HTTP call to the session's activity log."""
        start = response.request.extensions.get("_log_start", 0)
        duration_ms = int((time.perf_counter() - start) * 1000)
        log_session_event(
            session,
            method=str(response.request.method),
            url=str(response.request.url),
            status=response.status_code,
            duration_ms=duration_ms,
            source="windchill",
        )

    hooks = http_client.event_hooks
    hooks["request"].append(_on_request)
    hooks["response"].append(_on_response)
    http_client.event_hooks = hooks

    client._instrumented = True


import logging as _logging

_logger = _logging.getLogger(__name__)


def _close_client_safe(session: UserSession) -> None:
    """Close WRSClient/httpx.Client, swallowing errors."""
    try:
        session.client.close()
    except Exception:
        _logger.debug("Error closing client for session %s", session.token[:8], exc_info=True)


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, UserSession] = {}
        self._lock = threading.Lock()
        self._reaper_started = False

    def _start_reaper(self) -> None:
        """Start background thread that cleans up expired sessions every 60s."""
        if self._reaper_started:
            return
        self._reaper_started = True

        def _reap() -> None:
            while True:
                time.sleep(60)
                self._evict_expired()

        t = threading.Thread(target=_reap, daemon=True, name="session-reaper")
        t.start()

    def _evict_expired(self) -> None:
        """Remove all expired sessions and close their clients."""
        now = time.time()
        expired: list[UserSession] = []
        with self._lock:
            tokens_to_remove = [
                tok for tok, s in self._sessions.items() if s.expires_at < now
            ]
            for tok in tokens_to_remove:
                expired.append(self._sessions.pop(tok))
        for s in expired:
            _close_client_safe(s)
            _logger.info("Reaped expired session %s (user=%s)", s.token[:8], s.username)

    def create(
        self,
        system_key: str,
        system_url: str,
        username: str,
        client: WRSClient,
    ) -> UserSession:
        self._start_reaper()
        token = secrets.token_urlsafe(32)
        session = UserSession(
            token=token,
            system_key=system_key,
            system_url=system_url,
            username=username,
            client=client,
            expires_at=time.time() + settings.SESSION_TTL_SECONDS,
        )
        instrument_client_requests(session)
        with self._lock:
            self._sessions[token] = session
        return session

    def get(self, token: str | None) -> UserSession | None:
        if not token:
            return None
        with self._lock:
            session = self._sessions.get(token)
            if not session:
                return None
            if session.expires_at < time.time():
                del self._sessions[token]
                # Close client outside the lock
                _close_client_safe(session)
                return None
            session.expires_at = time.time() + settings.SESSION_TTL_SECONDS
            return session

    def delete(self, token: str | None) -> None:
        if not token:
            return
        session: UserSession | None = None
        with self._lock:
            session = self._sessions.pop(token, None)
        if session:
            _close_client_safe(session)


session_store = SessionStore()
