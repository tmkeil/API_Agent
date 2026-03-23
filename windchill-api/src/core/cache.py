"""
TTL In-Memory-Cache.
Thread-sicher, kein externer Dependency (kein Redis nötig für den Start).
Für Produktionslast mit mehreren Prozessen auf Redis migrieren.
"""

import threading
import time
from typing import Any, Optional


class TTLCache:
    def __init__(self, maxsize: int = 1000, ttl: int = 60):
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()
        self._maxsize = maxsize
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if time.monotonic() < expires_at:
                return value
            del self._store[key]
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        effective_ttl = ttl if ttl is not None else self._ttl
        with self._lock:
            if len(self._store) >= self._maxsize:
                # Evict the entry with the earliest expiry
                oldest = min(self._store, key=lambda k: self._store[k][1])
                del self._store[oldest]
            self._store[key] = (value, time.monotonic() + effective_ttl)

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._store)


# Singleton used by the service layer — initialized from settings
def _create_cache() -> TTLCache:
    from src.core.config import settings
    return TTLCache(maxsize=settings.CACHE_MAX_SIZE, ttl=settings.CACHE_TTL_SECONDS)

cache = _create_cache()
