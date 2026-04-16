"""Windchill-API — FastAPI Application Entry Point."""

import logging
import os
import socket
import time
from contextlib import asynccontextmanager
from urllib.parse import urlparse

import httpx
import uvicorn
from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.adapters.wrs_client import WRSError
from src.core.config import WINDCHILL_SYSTEMS, settings
from src.core.auth import require_auth
from src.routers.parts import router as parts_router
from src.routers.auth import router as auth_router
from src.routers.search import router as search_router
from src.routers.admin import router as admin_router
from src.routers.change import router as change_router
from src.routers.documents import router as documents_router
from src.routers.versions import router as versions_router
from src.routers.write import router as write_router
from src.routers.bulk import router as bulk_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle — cleanup service-account client on exit."""
    yield
    # Shutdown: close the service-account singleton if it was created
    from src.adapters.wrs_client import _service_client
    if _service_client is not None:
        try:
            _service_client.close()
            logger.info("Service-account WRSClient closed.")
        except Exception:
            logger.debug("Error closing service client", exc_info=True)


app = FastAPI(
    title="Windchill API",
    description="API-Layer über PTC Windchill REST Services (WRS/OData).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — origins from settings (configurable via CORS_ORIGINS env var)
cors_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_timing_headers(request: Request, call_next) -> Response:
    t0 = time.monotonic()
    try:
        response = await call_next(request)
    except Exception:
        # Re-raise so FastAPI's exception handlers still fire
        raise
    elapsed_ms = round((time.monotonic() - t0) * 1000, 1)
    response.headers["X-Response-Time-Ms"] = str(elapsed_ms)

    if settings.LOG_TIMING:
        logger.info(
            "%s %s → %d (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
    return response


# ── Global exception handler — eliminates repetitive try/except in routers ──

@app.exception_handler(WRSError)
async def wrs_error_handler(request: Request, exc: WRSError):
    """Convert any unhandled WRSError to a structured JSON response."""
    return JSONResponse(
        status_code=exc.status_code or 502,
        content={"detail": str(exc)},
    )


app.include_router(auth_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(parts_router, prefix="/api")
app.include_router(change_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(versions_router, prefix="/api")
app.include_router(write_router, prefix="/api")
app.include_router(bulk_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


def _resolve_frontend_dist() -> str | None:
    """Return frontend dist directory if present in known runtime locations."""
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, "frontend-dist"),
        os.path.join(os.path.dirname(here), "windchill-frontend", "dist"),
    ]
    for path in candidates:
        if os.path.isdir(path):
            return path
    return None


_frontend_dist = _resolve_frontend_dist()
if _frontend_dist:
    app.mount("/assets", StaticFiles(directory=os.path.join(_frontend_dist, "assets")), name="frontend-assets")

    @app.get("/", include_in_schema=False)
    def serve_frontend_index() -> FileResponse:
        return FileResponse(os.path.join(_frontend_dist, "index.html"))


    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_frontend_spa(full_path: str) -> Response:
        if full_path.startswith("api/") or full_path in {"docs", "redoc", "openapi.json", "health", "health/windchill"}:
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        requested = os.path.join(_frontend_dist, full_path)
        if os.path.isfile(requested):
            return FileResponse(requested)
        return FileResponse(os.path.join(_frontend_dist, "index.html"))


@app.get("/health", tags=["meta"], include_in_schema=False)
def health() -> dict:
    return {"status": "ok"}


@app.get("/health/windchill", tags=["meta"], dependencies=[Depends(require_auth)])
def health_windchill() -> dict:
    """Netzwerk-Konnektivitaetstest zu allen Windchill-Systemen.

    Probiert einen einfachen TCP-Connect + HTTP GET auf jedes
    konfigurierte System. Braucht Authentifizierung.
    """
    results = {}
    for key, url in WINDCHILL_SYSTEMS.items():
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        entry: dict = {"url": url, "host": host, "port": port}

        # TCP-Connect (DNS + Netzwerk)
        try:
            sock = socket.create_connection((host, port), timeout=5)
            sock.close()
            entry["tcp"] = "ok"
        except Exception as e:
            entry["tcp"] = f"FAIL: {type(e).__name__}: {e}"
            results[key] = entry
            continue

        # HTTP GET (TLS + Webserver)
        try:
            resp = httpx.get(
                f"{url}/servlet/odata/{settings.WRS_ODATA_VERSION}/ProdMgmt",
                verify=False,
                timeout=10,
                follow_redirects=True,
            )
            entry["http_status"] = resp.status_code
            entry["http_url"] = str(resp.url)
            entry["content_type"] = resp.headers.get("content-type", "")
        except Exception as e:
            entry["http"] = f"FAIL: {type(e).__name__}: {e}"

        results[key] = entry

    return {"systems": results}


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )