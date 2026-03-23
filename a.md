abc1
windchill-api/api.py
"""Windchill-API — FastAPI Application Entry Point."""

import logging
import time

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.routers.parts import router as parts_router
from src.routers.auth import router as auth_router
from src.routers.search import router as search_router
from src.routers.admin import router as admin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Windchill API",
    description="API-Layer über PTC Windchill REST Services (WRS/OData).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_timing_headers(request: Request, call_next) -> Response:
    t0 = time.monotonic()
    response = await call_next(request)
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


app.include_router(auth_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(parts_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/health", tags=["meta"], include_in_schema=False)
def health() -> dict:
    return {"status": "ok"}


@app.get("/health/windchill", tags=["meta"])
def health_windchill() -> dict:
    """Netzwerk-Konnektivitaetstest zu allen Windchill-Systemen.

    Probiert einen einfachen TCP-Connect + HTTP GET auf jedes
    konfigurierte System. Braucht KEINE Credentials.
    """
    import socket
    from urllib.parse import urlparse

    import httpx

    from src.core.config import WINDCHILL_SYSTEMS

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
                f"{url}/servlet/odata/v6/ProdMgmt",
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
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)













abc1
windchill-api/src/adapters/base.py
"""
WRS Client — Basis-Klasse mit HTTP-Infrastruktur und Authentifizierung.
======================================================================

Enthaelt:
  - WRSError Exception
  - WRSClientBase: __init__, Verbindung, Auth, HTTP-Methoden (_raw_get, _get,
    _get_json, _get_all_pages), close().

Die fachlichen Methoden (Parts, BOM, Dokumente, …) werden in separaten
Mixin-Klassen definiert und in ``wrs_client.py`` zusammengesetzt.
"""

import logging
import threading
import time
from typing import Any, Optional

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════
# Exceptions
# ═════════════════════════════════════════════════════════════

class WRSError(Exception):
    """Fehler beim Zugriff auf Windchill REST Services.

    Attributes:
        status_code: HTTP-Statuscode (falls vorhanden), z.B. 401, 404, 502.
    """

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


# ═════════════════════════════════════════════════════════════
# Base Client
# ═════════════════════════════════════════════════════════════

class WRSClientBase:
    """HTTP-Infrastruktur und Authentifizierung fuer die Windchill OData API.

    Lifecycle:
        client = WRSClient(base_url, user, pw)   # verbindet + authentifiziert
        parts  = client.search_parts("BAL*")      # OData-Abfrage
        client.close()                             # httpx-Session schliessen

    Der Konstruktor ruft sofort _connect() auf und wirft WRSError,
    wenn die Verbindung oder Authentifizierung fehlschlaegt.
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        *,
        odata_version: str = "v6",
        verify_tls: bool = False,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.odata_base = f"{self.base_url}/servlet/odata/{odata_version}"
        self._timeout = timeout
        self._max_retries = max_retries
        self._username = username
        self._password = password

        # httpx-Session OHNE globalen auth-Header.
        # Grund: Bei Form-Auth schickt Windchill eine Session-Cookie.
        # Wenn gleichzeitig ein Basic-Auth-Header mitkommt, verwirft
        # Windchill die Cookie und versucht Basic Auth → 401.
        # Basic Auth wird nur im Verbindungstest einmalig explizit gesetzt.
        self._http = httpx.Client(
            verify=verify_tls,
            timeout=timeout,
            follow_redirects=True,
            headers={"Accept": "application/json"},
        )
        self._lock = threading.Lock()

        # Caches & OData-Discovery (werden pro Client-Instanz gefuellt)
        self._part_cache: dict[str, dict] = {}
        self._bom_nav_strategy: Optional[tuple[str, bool]] = None
        self._usage_link_nav: Optional[str] = None
        self._part_properties: list[str] = []
        self._doc_service_available: bool = True

        self._connect()

    # ── Verbindung & Authentifizierung ───────────────────────

    def _connect(self) -> None:
        """Verbindung herstellen, Auth-Verfahren erkennen und authentifizieren.

        Ablauf:
          1. GET /ProdMgmt mit Basic Auth → pruefen ob Server antwortet.
          2. Antwort auswerten:
             a) 200 + JSON            → Basic Auth akzeptiert → dauerhaft aktivieren.
             b) 401 + WWW-Authenticate: Basic → Credentials falsch → sofort Fehler.
             c) Redirect/HTML/j_security_check → Form Login noetig.
          3. Nach erfolgreichem Login: Part-Properties discovern.

        Raises:
            WRSError: Keine Verbindung oder Authentifizierung fehlgeschlagen.
        """
        logger.info("Connecting to %s", self.odata_base)

        # Schritt 1: Verbindungstest mit explizitem Basic-Auth
        try:
            resp = self._http.get(
                f"{self.odata_base}/ProdMgmt",
                auth=(self._username, self._password),
                timeout=15,
            )
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
            logger.error(
                "Verbindung zu Windchill fehlgeschlagen: %s — %s",
                type(e).__name__, e,
            )
            raise WRSError(
                f"Keine Verbindung zu {self.base_url}: {type(e).__name__}: {e}",
                status_code=502,
            )

        content_type = resp.headers.get("content-type", "").lower()
        www_auth = resp.headers.get("www-authenticate", "").lower()

        # Ausfuehrliches Logging fuer Diagnose bei Auth-Problemen
        logger.info(
            "Auth-Probe: status=%d url=%s content-type=%s www-authenticate=%s",
            resp.status_code, resp.url, content_type, www_auth,
        )

        # Schritt 2a: Basic Auth akzeptiert (Erfolg)
        if resp.status_code < 400 and "text/html" not in content_type:
            logger.info("Basic Auth akzeptiert (status=%d)", resp.status_code)
            self._http.auth = (self._username, self._password)
            self._discover_part_properties()
            return

        # Schritt 2b: Server-Fehler (5xx) → System ist nicht verfuegbar
        # Wichtig: VOR dem Form-Auth-Check, weil 503 oft text/html liefert
        # und sonst faelschlicherweise als Login-Seite interpretiert wird.
        if resp.status_code >= 500:
            raise WRSError(
                f"Windchill nicht verfügbar (HTTP {resp.status_code}). "
                f"Das System ist möglicherweise in Wartung oder nicht gestartet.",
                status_code=resp.status_code,
            )

        # Schritt 2c: Server verlangt Basic Auth → Credentials sind falsch
        # Der WWW-Authenticate Header zeigt an, dass Basic Auth der gewuenschte
        # Mechanismus ist. Dann ist ein 401 kein Grund fuer Form-Login.
        if resp.status_code == 401 and "basic" in www_auth:
            raise WRSError(
                "Authentifizierung fehlgeschlagen – Benutzer oder Passwort falsch.",
                401,
            )

        # Schritt 2d: Login-Seite / j_security_check → Form Auth
        if "j_security_check" in str(resp.url) or "text/html" in content_type:
            self._authenticate_form()
            self._verify_authenticated()
            self._discover_part_properties()
            return

        # Schritt 2e: Unerwartete Antwort (z.B. Proxy-Fehlerseite, SSO)
        raise WRSError(
            f"Unerwartete Antwort von Windchill: HTTP {resp.status_code}, "
            f"content-type={content_type}, url={resp.url}",
            resp.status_code,
        )

    def _authenticate_form(self) -> None:
        """Java EE Form-based Authentication (j_security_check).

        POST an /Windchill/j_security_check mit:
          - j_username: Benutzername (Java EE Standard-Feldname)
          - j_password: Passwort    (Java EE Standard-Feldname)

        Das 'j_' Praefix ist Teil der Java Servlet Specification.
        Nach erfolgreichem Login setzt Windchill eine Session-Cookie
        und optional einen CSRF_NONCE Header fuer Write-Operationen.
        """
        logger.info("Form Login erforderlich — sende j_security_check")
        try:
            resp = self._http.post(
                f"{self.base_url}/j_security_check",
                data={
                    "j_username": self._username,
                    "j_password": self._password,
                },
                follow_redirects=True,
            )
            # CSRF-Token fuer spaetere Write-Requests merken
            nonce = resp.headers.get("CSRF_NONCE")
            if nonce:
                self._http.headers["CSRF_NONCE"] = nonce
            logger.info("Form Login: status=%d url=%s", resp.status_code, resp.url)
        except Exception as e:
            raise WRSError(f"Form Login fehlgeschlagen: {e}")

    def _verify_authenticated(self) -> None:
        """Pruefen ob die Session nach Form-Login gueltig ist.

        Ein GET ohne Basic-Auth-Header — nur die Session-Cookie wird gesendet.
        Prueft nicht nur 401, sondern auch ob die Antwort JSON (OData) ist.
        Windchill kann bei fehlgeschlagenem Form-Login mit 200 + HTML antworten
        (Login-Seite nochmal), was kein echter Erfolg ist.
        """
        try:
            resp = self._raw_get(f"{self.odata_base}/ProdMgmt", timeout=15)
        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
            logger.error(
                "Verify-Auth Verbindung fehlgeschlagen: %s — %s",
                type(e).__name__, e,
            )
            raise WRSError(f"Keine Verbindung zu {self.base_url}: {type(e).__name__}: {e}")

        content_type = resp.headers.get("content-type", "").lower()

        logger.info(
            "Verify-Auth: status=%d url=%s content-type=%s",
            resp.status_code, resp.url, content_type,
        )

        if resp.status_code == 401:
            raise WRSError(
                "Authentifizierung fehlgeschlagen – Benutzer oder Passwort falsch.",
                401,
            )

        # Form-Login kann mit 200 OK antworten, aber die Login-Seite
        # nochmal ausliefern statt OData-JSON.
        if "j_security_check" in str(resp.url) or "text/html" in content_type:
            raise WRSError(
                "Authentifizierung fehlgeschlagen – Login-Seite statt OData-JSON erhalten.",
                401,
            )

    def _discover_part_properties(self) -> None:
        """Fragt einen einzelnen Part ab um die verfuegbaren Property-Namen zu lernen.

        Diese Informationen werden spaeter fuer $select-Optimierungen genutzt.
        Fehler werden nur geloggt — das Feature ist optional.
        """
        try:
            resp = self._raw_get(
                f"{self.odata_base}/ProdMgmt/Parts",
                params={"$top": "1"},
            )
            if resp.status_code == 200:
                items = resp.json().get("value", [])
                if items:
                    self._part_properties = list(items[0].keys())
                    logger.info(
                        "%d Part-Properties discovered", len(self._part_properties)
                    )
        except Exception as e:
            logger.warning("Part-Properties konnten nicht ermittelt werden: %s", e)

    # ── Low-level HTTP ───────────────────────────────────────

    def _raw_get(self, url: str, params: Any = None, timeout: float | None = None) -> httpx.Response:
        """Einzelner GET-Request ohne Retry-Logik.

        Synchronisiert den CSRF_NONCE Header — Windchill kann ihn bei
        jedem Response aktualisieren, und Write-Requests benoetigen
        immer den aktuellsten Wert.
        """
        resp = self._http.get(
            url,
            params=params,
            timeout=timeout or self._timeout,
        )
        nonce = resp.headers.get("CSRF_NONCE")
        if nonce:
            self._http.headers["CSRF_NONCE"] = nonce
        return resp

    def _get(
        self,
        url: str,
        params: Any = None,
        *,
        suppress_errors: bool = False,
    ) -> Optional[httpx.Response]:
        """GET mit Exponential-Backoff Retry (max. self._max_retries Versuche).

        Args:
            url:              Vollstaendige OData-URL.
            params:           Query-Parameter (z.B. $filter, $top).
            suppress_errors:  True → gibt None zurueck statt Exception zu werfen.

        Returns:
            httpx.Response bei Erfolg (status < 500), sonst None oder WRSError.
        """
        delay = 1.0
        last_exc: Optional[Exception] = None

        for attempt in range(self._max_retries):
            try:
                resp = self._raw_get(url, params)
                if resp.status_code < 500:
                    return resp
                last_exc = WRSError(f"Server error {resp.status_code}", resp.status_code)
            except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError) as e:
                last_exc = WRSError(f"Connection error: {e}")

            if attempt < self._max_retries - 1:
                time.sleep(delay)
                delay = min(delay * 2, 10.0)

        if suppress_errors:
            return None
        raise last_exc or WRSError("Unknown error")

    def _get_json(self, url: str, params: Any = None) -> dict:
        """GET → JSON dict. Wirft WRSError bei HTTP != 200."""
        resp = self._get(url, params)
        if resp is None or resp.status_code != 200:
            status = resp.status_code if resp else 502
            raise WRSError(f"HTTP {status}", status)
        return resp.json()

    def _get_all_pages(
        self,
        url: str,
        params: Any = None,
        *,
        max_pages: int = 200,
        return_none_on_error: bool = False,
    ) -> Optional[list]:
        """OData-Paging: Folgt @odata.nextLink bis alle Seiten geladen sind.

        Args:
            return_none_on_error: True → None bei Fehler (statt leerer Liste).
                                  Damit kann der Aufrufer unterscheiden zwischen
                                  'keine Ergebnisse' ([]) und 'Fehler' (None).
        """
        try:
            resp = self._get(url, params, suppress_errors=True)
            if resp is None or resp.status_code != 200:
                return None if return_none_on_error else []

            data = resp.json()
            all_items = list(data.get("value", []))

            page = 1
            while "@odata.nextLink" in data and page < max_pages:
                page += 1
                resp = self._get(data["@odata.nextLink"], suppress_errors=True)
                if resp is None or resp.status_code != 200:
                    break
                data = resp.json()
                all_items.extend(data.get("value", []))

            return all_items
        except Exception:
            logger.debug("_get_all_pages(%s) failed", url, exc_info=True)
            return None if return_none_on_error else []

    # ── Lifecycle ────────────────────────────────────────────

    def close(self) -> None:
        """httpx-Session schliessen und Ressourcen freigeben."""
        self._http.close()















abc1
windchill-api/src/adapters/bom_mixin.py
"""
WRS Client — BOM-Operationen (Mixin).
======================================

Stuecklistenstruktur laden: Usage-Links, Kind-Parts aufloesen.
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class BomMixin:
    """BOM / Stuecklisten-Operationen (Mixin fuer WRSClientBase)."""

    def get_bom_children(self: "WRSClientBase", part_id: str) -> list:
        """BOM-Kinder (Usage Links) eines Parts laden.

        Windchill bietet mehrere OData-Navigations-Properties fuer die
        Stuecklistenstruktur. Welche verfuegbar ist, haengt von der
        WRS/OData-Version ab:
          - Uses           (Standard, v5+)
          - UsesInterface  (alternative Struktur)
          - BOMComponents  (aeltere Versionen)
          - PartStructure  (Fallback)

        Die erste funktionierende Strategie wird gecacht und fuer
        alle weiteren Abfragen dieser Session wiederverwendet.
        """
        nav_options = ["Uses", "UsesInterface", "BOMComponents", "PartStructure"]

        # Gecachte Strategie aus vorherigem Aufruf verwenden
        if self._bom_nav_strategy:
            nav, use_expand = self._bom_nav_strategy
            url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/{nav}"
            params = {"$expand": "Uses"} if use_expand else None
            result = self._get_all_pages(url, params, return_none_on_error=True)
            if result is not None:
                return result
            # Strategie hat nicht funktioniert → neu discovern
            self._bom_nav_strategy = None

        # Alle Strategien durchprobieren
        for nav in nav_options:
            url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/{nav}"

            # Zuerst mit $expand=Uses (liefert Kind-Parts inline mit)
            result = self._get_all_pages(url, {"$expand": "Uses"}, return_none_on_error=True)
            if result is not None:
                self._bom_nav_strategy = (nav, True)
                return result

            # Ohne $expand (Kind-Parts muessen einzeln aufgeloest werden)
            result = self._get_all_pages(url, return_none_on_error=True)
            if result is not None:
                self._bom_nav_strategy = (nav, False)
                return result

        return []

    def resolve_usage_link_child(self: "WRSClientBase", link: dict) -> Optional[dict]:
        """Kind-Part aus einem BOM Usage-Link aufloesen.

        Ein Usage-Link beschreibt die Beziehung Parent→Child in der Stueckliste.
        Das Kind-Part-Objekt kann entweder:
          a) Bereits inline im Link enthalten sein ($expand hat funktioniert)
          b) Per Navigation-Property nachgeladen werden muessen

        Probiert die Keys: Uses, RoleBObject, Child, Part.
        """
        # Pruefen ob das Kind bereits inline vorhanden ist
        for key in ["Uses", "RoleBObject", "Child", "Part"]:
            child = link.get(key)
            if isinstance(child, dict) and ("Number" in child or "ID" in child):
                return child

        # Kind per Navigation-Property nachladen
        link_id = link.get("ID", "")
        if not link_id:
            return None

        # Gecachte Navigation verwenden
        if self._usage_link_nav:
            child = self._resolve_link_via_nav(link_id, self._usage_link_nav)
            if child:
                return child
            self._usage_link_nav = None  # Funktioniert nicht mehr → neu discovern

        # Alle Navigation-Properties durchprobieren
        for nav in ["Uses", "RoleBObject", "Child"]:
            child = self._resolve_link_via_nav(link_id, nav)
            if child:
                self._usage_link_nav = nav
                return child

        return None

    def _resolve_link_via_nav(self: "WRSClientBase", link_id: str, nav: str) -> Optional[dict]:
        """Hilfsmethode: Kind-Part ueber ein bestimmtes Navigation-Property laden."""
        url = f"{self.odata_base}/ProdMgmt/UsageLinks('{link_id}')/{nav}"
        try:
            data = self._get_json(url)
            # OData kann Collection oder einzelnes Objekt liefern
            if "value" in data and data["value"]:
                return data["value"][0]
            if "ID" in data or "Number" in data:
                return data
        except Exception:
            logger.debug("_resolve_link_via_nav(%s, %s) failed", link_id, nav, exc_info=True)
        return None















abc1
windchill-api/src/adapters/documents_mixin.py
"""
WRS Client — Dokument-Operationen (Mixin).
============================================

Beschriebene Dokumente und CAD-Dokumente eines Parts laden.
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class DocumentsMixin:
    """Dokument-spezifische Operationen (Mixin fuer WRSClientBase)."""

    def get_described_documents(self: "WRSClientBase", part_id: str, part_number: str = "") -> list:
        """Dokumente laden, die mit einem Part verknuepft sind.

        Drei Quellen in Prioritaetsreihenfolge:
          1. DescribedBy-Navigation    (Standard-Verknuepfung Part → Dokument)
          2. DocMgmt + BALREFERENCEPART (firmenspezifischer Balluff-Filter)
          3. References-Navigation     (Fallback fuer aeltere WRS-Versionen)
        """
        all_docs: list[dict] = []
        seen: set[str] = set()

        def _collect(items: Optional[list]) -> None:
            if not items:
                return
            for item in items:
                doc_id = item.get("ID", "")
                if doc_id and doc_id not in seen:
                    seen.add(doc_id)
                    all_docs.append(item)

        # Quelle 1: DescribedBy
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/DescribedBy"
        _collect(self._get_all_pages(url, return_none_on_error=True))

        # Quelle 2: DocMgmt mit Balluff-spezifischem Filter
        if part_number and self._doc_service_available:
            safe = part_number.replace("'", "''")
            url = f"{self.odata_base}/DocMgmt/Documents"
            result = self._get_all_pages(
                url,
                {"$filter": f"BALREFERENCEPART/any(s:s eq '{safe}')"},
                return_none_on_error=True,
            )
            if result is not None:
                _collect(result)
            else:
                # DocMgmt-Service nicht verfuegbar → nicht nochmal versuchen
                self._doc_service_available = False

        # Quelle 3: Fallback — References
        if not all_docs:
            url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/References"
            _collect(self._get_all_pages(url, return_none_on_error=True))

        return all_docs

    def get_cad_documents(self: "WRSClientBase", part_id: str) -> list:
        """CAD-Dokumente (EPM/CAD) eines Parts laden.

        Zwei Quellen:
          1. PartDocAssociations + $expand=RelatedCADDoc (bevorzugt)
          2. Representations (Fallback)
        """
        all_cads: list[dict] = []
        seen: set[str] = set()

        # Quelle 1: PartDocAssociations mit inline-Expand
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/PartDocAssociations"
        result = self._get_all_pages(url, {"$expand": "RelatedCADDoc"}, return_none_on_error=True)
        if result:
            for assoc in result:
                cad = assoc.get("RelatedCADDoc") or {}
                cad_id = cad.get("ID", "")
                if cad_id and cad_id not in seen and (cad.get("Number") or cad.get("Name")):
                    seen.add(cad_id)
                    all_cads.append(cad)

        # Quelle 2: Fallback — Representations
        if not all_cads:
            url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/Representations"
            result = self._get_all_pages(url, return_none_on_error=True)
            if result:
                for cad in result:
                    cad_id = cad.get("ID", "")
                    if cad_id and cad_id not in seen:
                        seen.add(cad_id)
                        all_cads.append(cad)

        return all_cads















abc1
windchill-api/src/adapters/parts_mixin.py
"""
WRS Client — Part-Operationen (Mixin).
=======================================

Methoden fuer Einzel-Part-Suche, ID-Lookup, Freitextsuche und Soft-Attributes.
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from src.core.odata import extract_id

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class PartsMixin:
    """Part-spezifische Operationen (Mixin fuer WRSClientBase)."""

    # ── Part-Suche ───────────────────────────────────────────

    def find_part(self: "WRSClientBase", part_number: str) -> dict:
        """Part nach Nummer suchen (neuste Version/Iteration).

        Versucht mehrere OData-Filter in absteigender Praezision:
          1. Exakte Nummer
          2. Exakte Nummer + LatestIteration
          3. contains (Teilstring)
          4. startswith

        Returns:
            Dict mit allen Part-Properties.
        Raises:
            WRSError(404): Part nicht gefunden.
        """
        from src.adapters.base import WRSError

        if part_number in self._part_cache:
            return self._part_cache[part_number]

        url = f"{self.odata_base}/ProdMgmt/Parts"
        safe = part_number.replace("'", "''")

        filters = [
            f"Number eq '{safe}'",
            f"Number eq '{safe}' and LatestIteration eq true",
            f"contains(Number,'{safe}')",
            f"startswith(Number,'{safe}')",
        ]

        for filt in filters:
            resp = self._get(url, {"$filter": filt}, suppress_errors=True)
            if resp and resp.status_code == 200:
                items = resp.json().get("value", [])
                if items:
                    # Neuste Version + Iteration zuerst
                    items.sort(
                        key=lambda p: (p.get("Version", ""), p.get("Iteration", "")),
                        reverse=True,
                    )
                    self._part_cache[part_number] = items[0]
                    return items[0]

        raise WRSError(f"Part '{part_number}' nicht in Windchill gefunden", 404)

    def get_part_by_id(self: "WRSClientBase", part_id: str) -> Optional[dict]:
        """Part nach interner OData-ID laden."""
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')"
        try:
            return self._get_json(url)
        except Exception:
            logger.debug("get_part_by_id(%s) failed", part_id, exc_info=True)
            return None

    def search_parts(self: "WRSClientBase", query: str, limit: int = 25) -> list[dict]:
        """Freitextsuche nach Parts (Nummer oder Name).

        Kombiniert mehrere OData-Filter um moeglichst viele Treffer zu finden:
          1. Exakte Nummer    (schnell, hoechste Relevanz)
          2. Nummer enthaelt  (breit)
          3. Name enthaelt    (breit)
        """
        url = f"{self.odata_base}/ProdMgmt/Parts"
        collected: dict[str, dict] = {}
        safe = query.replace("'", "''")

        strategies = [
            {"$filter": f"Number eq '{safe}'", "$top": "20"},
            {"$filter": f"contains(Number,'{safe}')", "$top": "100"},
            {"$filter": f"contains(Name,'{safe}')", "$top": "100"},
        ]

        for params in strategies:
            try:
                items = self._get_all_pages(url, params)
                for item in items:
                    pid = extract_id(item)
                    if pid:
                        collected[str(pid)] = item
                if len(collected) >= 250:
                    break
            except Exception:
                logger.debug("search_parts filter failed: %s", params, exc_info=True)
                continue

        return list(collected.values())[:limit]

    # ── Soft Attributes ──────────────────────────────────────

    def get_soft_attributes(self: "WRSClientBase", part_id: str, attr_names: list[str]) -> dict:
        """Custom-Attribute (IBAs / Soft Attributes) eines Parts laden.

        IBAs sind firmenspezifische Attribute (z.B. BALMADEFROMNUMBER),
        die ueber $select abgefragt werden koennen.
        Fallback: Gesamten Part laden falls $select nicht unterstuetzt wird.
        """
        result = {name: "" for name in attr_names}
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')"

        # Versuch 1: Gezieltes $select (schneller, weniger Daten)
        try:
            resp = self._get(url, {"$select": ",".join(attr_names)}, suppress_errors=True)
            if resp and resp.status_code == 200:
                data = resp.json()
                for name in attr_names:
                    val = data.get(name, "")
                    if isinstance(val, dict):
                        val = val.get("Value", val.get("Display", ""))
                    if val:
                        result[name] = str(val)
                if any(result.values()):
                    return result
        except Exception:
            logger.debug("get_soft_attributes $select failed for %s", part_id, exc_info=True)

        # Versuch 2: Alle Properties laden (Fallback)
        try:
            data = self._get_json(url)
            for name in attr_names:
                val = data.get(name, "")
                if isinstance(val, dict):
                    val = val.get("Value", val.get("Display", ""))
                if val:
                    result[name] = str(val)
        except Exception:
            logger.debug("get_soft_attributes full-load failed for %s", part_id, exc_info=True)

        return result















abc1
windchill-api/src/adapters/search_mixin.py
"""
WRS Client — Multi-Entity-Suche (Mixin).
=========================================

Suche ueber beliebige Windchill-Objekttypen (Parts, Dokumente, CAD, Change, …).
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.core.odata import extract_id

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class SearchMixin:
    """Multi-Entity-Suche (Mixin fuer WRSClientBase)."""

    # Mapping: type_key → (OData service, entity set, Windchill type label)
    SEARCHABLE_ENTITIES: dict[str, tuple[str, str, str]] = {
        "part":            ("ProdMgmt",          "Parts",           "WTPart"),
        "document":        ("DocMgmt",           "Documents",       "WTDocument"),
        "cad_document":    ("CADDocumentMgmt",   "CADDocuments",    "EPMDocument"),
        "change_notice":   ("ChangeMgmt",        "ChangeNotices",   "WTChangeOrder2"),
        "change_request":  ("ChangeMgmt",        "ChangeRequests",  "WTChangeRequest2"),
        "problem_report":  ("ChangeMgmt",        "ProblemReports",  "WTChangeIssue"),
    }

    def find_object(self: "WRSClientBase", type_key: str, number: str) -> dict:
        """Ein Windchill-Objekt beliebigen Typs anhand seiner Nummer finden.

        Args:
            type_key: Schluessel aus SEARCHABLE_ENTITIES (z.B. 'part', 'document').
            number:   Objektnummer (z.B. '2200500023').

        Returns:
            OData-Dict des Objekts, ergaenzt um '_entity_type' und '_entity_type_key'.

        Raises:
            WRSError 404 wenn nicht gefunden, 400 wenn Typ unbekannt.
        """
        from src.adapters.base import WRSError

        if type_key not in self.SEARCHABLE_ENTITIES:
            raise WRSError(f"Unbekannter Objekttyp: '{type_key}'", status_code=400)

        service, entity_set, wc_type = self.SEARCHABLE_ENTITIES[type_key]
        url = f"{self.odata_base}/{service}/{entity_set}"
        safe = number.replace("'", "''")

        filters = [
            f"Number eq '{safe}'",
            f"contains(Number,'{safe}')",
        ]

        for filt in filters:
            resp = self._get(url, {"$filter": filt}, suppress_errors=True)
            if resp and resp.status_code == 200:
                items = resp.json().get("value", [])
                if items:
                    items.sort(
                        key=lambda p: (p.get("Version", ""), p.get("Iteration", "")),
                        reverse=True,
                    )
                    result = items[0]
                    result["_entity_type"] = wc_type
                    result["_entity_type_key"] = type_key
                    return result

        raise WRSError(
            f"{wc_type} '{number}' nicht in Windchill gefunden", status_code=404
        )

    def search_entities(
        self: "WRSClientBase",
        query: str,
        entity_types: list[str] | None = None,
        limit: int = 200,
    ) -> list[dict]:
        """Suche ueber mehrere Windchill-Entity-Typen gleichzeitig.

        Args:
            query:        Suchbegriff (Nummer oder Name, mit Wildcard * oder ?).
            entity_types: Liste von Typ-Keys (z.B. ["part","document"]).
                          None → alle Typen durchsuchen.
            limit:        Max. Gesamtergebnisse.

        Returns:
            Liste von OData-Dicts, ergaenzt um '_entity_type' (z.B. 'WTPart').
        """
        if entity_types is None:
            targets = list(self.SEARCHABLE_ENTITIES.items())
        else:
            targets = [
                (k, v) for k, v in self.SEARCHABLE_ENTITIES.items()
                if k in entity_types
            ]

        safe = query.replace("'", "''")
        collected: list[dict] = []
        seen_ids: set[str] = set()

        for type_key, (service, entity_set, wc_type) in targets:
            url = f"{self.odata_base}/{service}/{entity_set}"

            # OData-Filter: exakt, contains Number, contains Name
            filters = [
                {"$filter": f"Number eq '{safe}'", "$top": "20"},
                {"$filter": f"contains(Number,'{safe}')", "$top": "100"},
                {"$filter": f"contains(Name,'{safe}')", "$top": "100"},
            ]

            for params in filters:
                try:
                    items = self._get_all_pages(url, params, return_none_on_error=True)
                    if items is None:
                        # Service or entity set not available → skip remaining filters
                        break
                    for item in items:
                        pid = extract_id(item)
                        if pid and pid not in seen_ids:
                            seen_ids.add(pid)
                            item["_entity_type"] = wc_type
                            item["_entity_type_key"] = type_key
                            collected.append(item)
                except Exception:
                    logger.debug("search_entities failed for %s/%s", service, entity_set, exc_info=True)
                    continue

                if len(collected) >= limit:
                    break

            if len(collected) >= limit:
                break

        return collected[:limit]















abc1
windchill-api/src/adapters/where_used_mixin.py
"""
WRS Client — Where-Used / Einsatzverwendung (Mixin).
=====================================================

In welchen Parent-Baugruppen ist ein Part verbaut?
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.core.odata import extract_id

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class WhereUsedMixin:
    """Einsatzverwendung (Where-Used) — Mixin fuer WRSClientBase."""

    def get_where_used(self: "WRSClientBase", part_id: str) -> list[dict]:
        """Einsatzverwendung (Where-Used): in welchen Parent-Parts ist dieses Teil verbaut?

        Versucht mehrere OData-Pfade:
          1. PTC.ProdMgmt.GetWhereUsed Action (Windchill 12+)
          2. UsedBy Navigation Property
          3. UsageLinks mit $expand auf Uses (Reverse-Lookup)

        Returns:
            Liste von dicts mit Parent-Part-Informationen.
        """
        results: list[dict] = []
        seen: set[str] = set()

        # Strategie 1: GetWhereUsed Action
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/PTC.ProdMgmt.GetWhereUsed"
        resp = self._get(url, suppress_errors=True)
        if resp and resp.status_code == 200:
            data = resp.json()
            items = data.get("value", [])
            if isinstance(items, list):
                for item in items:
                    pid = extract_id(item)
                    if pid and pid not in seen:
                        seen.add(pid)
                        results.append(item)
            if results:
                return results

        # Strategie 2: UsedBy Navigation Property
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/UsedBy"
        items = self._get_all_pages(url, return_none_on_error=True)
        if items:
            for link in items:
                # UsedBy links point to the parent; try to resolve
                parent = link.get("Uses") or link.get("UsedBy") or link
                pid = extract_id(parent)
                if pid and pid not in seen:
                    seen.add(pid)
                    # If it's a link, try expanding to get the parent part
                    parent_data = self.get_part_by_id(pid) if not parent.get("Number") else parent
                    if parent_data:
                        results.append(parent_data)
            if results:
                return results

        # Strategie 3: UsageLinks mit $filter auf Uses Part
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/UsageLinks"
        items = self._get_all_pages(url, {"$expand": "Uses"}, return_none_on_error=True)
        if items:
            for link in items:
                parent = link.get("Uses") or {}
                pid = extract_id(parent)
                if pid and pid not in seen:
                    seen.add(pid)
                    results.append(parent)

        return results















abc1
windchill-api/src/adapters/wrs_client.py
"""
WRS (Windchill REST Services) HTTP-Adapter.
============================================

Zentraler HTTP-Client fuer die PTC Windchill OData REST API.

Zwei Betriebsmodi:
  1. Per-User-Instanz  — Frontend-Login mit eigenen Credentials pro Session.
  2. Service-Account    — Singleton fuer API-Key-geschuetzte Endpoints.

Authentifizierung:
  Windchill unterstuetzt zwei Auth-Verfahren. Welches aktiv ist, haengt
  von der Server-Konfiguration ab (nicht vom Client):
  - Basic Auth:  Standard HTTP Authorization Header.
  - Form Auth:   Java EE j_security_check (POST mit j_username / j_password).
                  Danach laeuft die Session ueber Cookies — kein Auth-Header mehr.

  Der Client erkennt automatisch welches Verfahren noetig ist und wechselt
  entsprechend (siehe _connect / _authenticate_basic / _authenticate_form).

OData-Patterns aus dem Stakeholder-Prototyp (BomProcessing_BOM_WEB_Export_V1).

Modulstruktur:
  - base.py            → WRSClientBase (HTTP, Auth, OData-Paging)
  - parts_mixin.py     → Part-Suche, Soft-Attributes
  - search_mixin.py    → Multi-Entity-Suche
  - bom_mixin.py       → BOM / Stueckliste
  - documents_mixin.py → Dokumente & CAD
  - where_used_mixin.py → Einsatzverwendung
  - wrs_client.py      → WRSClient (Zusammenbau) + Singleton
"""

import threading
from typing import Optional

from src.adapters.base import WRSClientBase, WRSError
from src.adapters.bom_mixin import BomMixin
from src.adapters.documents_mixin import DocumentsMixin
from src.adapters.parts_mixin import PartsMixin
from src.adapters.search_mixin import SearchMixin
from src.adapters.where_used_mixin import WhereUsedMixin
from src.core.config import settings

# Re-export damit bestehende Imports weiterhin funktionieren
__all__ = ["WRSClient", "WRSError", "get_service_client"]


# ═════════════════════════════════════════════════════════════
# Zusammengebauter Client
# ═════════════════════════════════════════════════════════════

class WRSClient(
    PartsMixin,
    SearchMixin,
    BomMixin,
    DocumentsMixin,
    WhereUsedMixin,
    WRSClientBase,
):
    """Vollstaendiger Windchill REST-Client.

    Kombiniert die Basis-Klasse (HTTP, Auth) mit allen fachlichen Mixins.
    Die Methoden-Reihenfolge (MRO) stellt sicher, dass Mixins die
    HTTP-Methoden der Basis-Klasse nutzen koennen.

    Lifecycle:
        client = WRSClient(base_url, user, pw)   # verbindet + authentifiziert
        parts  = client.search_parts("BAL*")      # OData-Abfrage
        client.close()                             # httpx-Session schliessen
    """
    pass


# ═════════════════════════════════════════════════════════════
# Service-Account Singleton
# ═════════════════════════════════════════════════════════════

_service_client: Optional[WRSClient] = None
_service_lock = threading.Lock()


def get_service_client() -> WRSClient:
    """Gibt einen Singleton-WRSClient mit Service-Account-Credentials zurueck.

    Verwendet die Werte aus .env (WRS_USERNAME, WRS_PASSWORD, WRS_BASE_URL).
    Thread-safe durch Double-Checked Locking.

    Raises:
        WRSError(401): Credentials nicht konfiguriert.
    """
    global _service_client
    if _service_client is not None:
        return _service_client

    with _service_lock:
        if _service_client is not None:
            return _service_client

        if not settings.WRS_USERNAME or not settings.WRS_PASSWORD:
            raise WRSError(
                "WRS_USERNAME / WRS_PASSWORD nicht konfiguriert. "
                "Bitte .env setzen oder Frontend-Session nutzen.",
                401,
            )

        _service_client = WRSClient(
            base_url=settings.WRS_BASE_URL,
            username=settings.WRS_USERNAME,
            password=settings.WRS_PASSWORD,
            odata_version=settings.WRS_ODATA_VERSION,
            verify_tls=settings.WRS_VERIFY_TLS,
            timeout=settings.WRS_TIMEOUT_SECONDS,
        )
        return _service_client


