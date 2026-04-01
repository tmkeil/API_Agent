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
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=40,
            ),
        )
        self._lock = threading.Lock()

        # OData-Discovery (werden pro Client-Instanz gefuellt)
        self._bom_nav_strategy: Optional[tuple[str, bool]] = None
        self._usage_link_nav: Optional[str] = None
        self._doc_service_available: bool = True

        try:
            self._connect()
        except Exception:
            self._http.close()
            raise

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
            with self._lock:
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

    def _get_all_pages_parallel(
        self,
        url: str,
        params: Any = None,
        *,
        max_pages: int = 40,
        max_workers: int = 10,
        return_none_on_error: bool = False,
    ) -> Optional[list]:
        """OData-Paging mit parallelem Abruf aller Seiten.

        Strategie:
        1. Erste Seite mit ``$count=true`` abrufen → liefert ``@odata.count``
           (Gesamtanzahl Treffer) und ``@odata.nextLink``.
        2. Aus ``@odata.count`` die exakte Seitenzahl berechnen.
        3. Alle verbleibenden Seiten parallel mit vorausberechneten
           Skiptokens abrufen (statt sequentiell auf nextLink zu warten).

        Windchill's Skiptokens sind einfache numerische Offsets (25, 50, 75 …).
        """
        import math
        import re as _re
        from concurrent.futures import ThreadPoolExecutor, as_completed

        try:
            # ── Seite 1 (mit $count=true) ─────────────────────
            p = dict(params or {})
            p["$count"] = "true"

            resp = self._get(url, p, suppress_errors=True)
            if resp is None or resp.status_code != 200:
                return None if return_none_on_error else []

            data = resp.json()
            first_page = list(data.get("value", []))
            next_link = data.get("@odata.nextLink")
            total_count = data.get("@odata.count")

            if not next_link or max_pages <= 1:
                return first_page

            # ── Skiptoken-Muster erkennen ─────────────────────
            m = _re.search(r'[\?&]\$skiptoken=(\d+)', next_link)
            if not m:
                # Kein numerischer Skiptoken → Fallback auf sequentiell
                return self._get_all_pages(
                    url, params,
                    max_pages=max_pages,
                    return_none_on_error=return_none_on_error,
                )

            skip_size = int(m.group(1))  # z.B. 25
            sep = next_link[m.start()]   # '?' oder '&'
            base_url = next_link[:m.start()]  # URL ohne $skiptoken

            # ── Exakte Seitenzahl aus @odata.count berechnen ──
            if total_count is not None and isinstance(total_count, (int, float)) and total_count > 0:
                needed_pages = min(math.ceil(int(total_count) / skip_size), max_pages)
            else:
                # Kein Count verfuegbar → Fallback auf max_pages
                needed_pages = max_pages

            logger.debug(
                "parallel paging: total_count=%s, skip_size=%s, needed_pages=%s, url=%s",
                total_count, skip_size, needed_pages, url,
            )

            # ── Nur benoetigte Seiten-URLs bauen ─────────────
            page_urls: list[tuple[int, str]] = []
            for pg in range(1, needed_pages):  # pg 0 = first_page, schon da
                st = skip_size * pg
                page_urls.append((pg, f"{base_url}{sep}$skiptoken={st}"))

            if not page_urls:
                return first_page

            # ── Parallel abrufen ──────────────────────────────
            results_by_page: dict[int, list[dict]] = {0: first_page}

            def _fetch(item: tuple[int, str]) -> tuple[int, list[dict]]:
                pg_num, pg_url = item
                r = self._get(pg_url, suppress_errors=True)
                if r is None or r.status_code != 200:
                    return pg_num, []
                return pg_num, list(r.json().get("value", []))

            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                futures = {pool.submit(_fetch, pu): pu for pu in page_urls}
                for future in as_completed(futures):
                    pg_num, items = future.result()
                    if items:
                        results_by_page[pg_num] = items

            # ── Ergebnisse in Seitenreihenfolge zusammenfuegen ─
            all_items: list[dict] = []
            for pg in sorted(results_by_page.keys()):
                all_items.extend(results_by_page[pg])

            return all_items

        except Exception:
            logger.debug("_get_all_pages_parallel(%s) failed", url, exc_info=True)
            return None if return_none_on_error else []

    def get_all_pages(
        self,
        url: str,
        params: Any = None,
        *,
        max_pages: int = 200,
        return_none_on_error: bool = False,
    ) -> Optional[list]:
        """Public wrapper for OData paging. See _get_all_pages."""
        return self._get_all_pages(
            url, params, max_pages=max_pages, return_none_on_error=return_none_on_error,
        )

    # ── Lifecycle ────────────────────────────────────────────

    def close(self) -> None:
        """httpx-Session schliessen und Ressourcen freigeben."""
        self._http.close()

    # ── Write-Operations (POST / PATCH / DELETE) ────────────

    def _refresh_csrf(self) -> None:
        """Frischen CSRF_NONCE von Windchill holen.

        Windchill rotiert den CSRF_NONCE serverseitig.  PTC-Dokumentation:
        GET mit Header ``CSRF_NONCE: fetch`` → Antwort enthaelt frischen Nonce.
        """
        old = self._http.headers.get("CSRF_NONCE", "")
        try:
            resp = self._http.get(
                f"{self.odata_base}/ProdMgmt/Parts",
                params={"$top": "0", "$select": "ID"},
                headers={"CSRF_NONCE": "fetch"},
                timeout=self._timeout,
            )
            nonce = resp.headers.get("CSRF_NONCE")
            if nonce:
                with self._lock:
                    self._http.headers["CSRF_NONCE"] = nonce
                logger.info("CSRF_NONCE refreshed: %s… → %s…", old[:12], nonce[:12])
            else:
                logger.warning(
                    "CSRF_NONCE refresh: kein Nonce in Antwort (status=%d, headers=%s)",
                    resp.status_code,
                    dict(resp.headers),
                )
        except Exception:
            logger.warning("_refresh_csrf fehlgeschlagen", exc_info=True)

    @staticmethod
    def _is_csrf_error(resp: httpx.Response) -> bool:
        """Erkennt Windchill CSRF-Fehler (400 mit 'security' in der Antwort)."""
        if resp.status_code != 400:
            return False
        try:
            text = resp.text.lower()
            return "security" in text or "csrf" in text
        except Exception:
            return False

    def _post(
        self,
        url: str,
        json_body: dict | None = None,
        *,
        suppress_errors: bool = False,
    ) -> Optional[httpx.Response]:
        """POST mit Retry, CSRF_NONCE Handling und CSRF-Retry.

        Bei CSRF-Fehler (400 + 'security') wird einmal automatisch
        ein frischer Nonce geholt und der Request wiederholt.
        """
        delay = 1.0
        last_exc: Optional[Exception] = None
        csrf_retried = False

        for attempt in range(self._max_retries):
            try:
                current_nonce = self._http.headers.get("CSRF_NONCE", "(none)")
                logger.info(
                    "POST attempt %d: %s — CSRF_NONCE=%s…",
                    attempt + 1, url, current_nonce[:12],
                )
                resp = self._http.post(
                    url,
                    json=json_body,
                    timeout=self._timeout,
                )
                resp_nonce = resp.headers.get("CSRF_NONCE")
                logger.info(
                    "POST response: status=%d, resp_CSRF_NONCE=%s",
                    resp.status_code,
                    (resp_nonce[:12] + "…") if resp_nonce else "(none)",
                )
                if resp_nonce:
                    with self._lock:
                        self._http.headers["CSRF_NONCE"] = resp_nonce

                # CSRF-Fehler: einmal refresh + retry
                if self._is_csrf_error(resp) and not csrf_retried:
                    logger.info("CSRF-Fehler bei POST %s — refreshe Nonce und wiederhole", url)
                    csrf_retried = True
                    self._refresh_csrf()
                    continue

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

    def _patch(
        self,
        url: str,
        json_body: dict | None = None,
        *,
        suppress_errors: bool = False,
    ) -> Optional[httpx.Response]:
        """PATCH mit Retry und CSRF_NONCE Handling + CSRF-Retry."""
        delay = 1.0
        last_exc: Optional[Exception] = None
        csrf_retried = False

        for attempt in range(self._max_retries):
            try:
                resp = self._http.patch(
                    url,
                    json=json_body,
                    timeout=self._timeout,
                )
                nonce = resp.headers.get("CSRF_NONCE")
                if nonce:
                    with self._lock:
                        self._http.headers["CSRF_NONCE"] = nonce

                if self._is_csrf_error(resp) and not csrf_retried:
                    logger.info("CSRF-Fehler bei PATCH %s — refreshe Nonce und wiederhole", url)
                    csrf_retried = True
                    self._refresh_csrf()
                    continue

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

    def _delete(
        self,
        url: str,
        *,
        suppress_errors: bool = False,
    ) -> Optional[httpx.Response]:
        """DELETE mit Retry und CSRF_NONCE Handling + CSRF-Retry."""
        delay = 1.0
        last_exc: Optional[Exception] = None
        csrf_retried = False

        for attempt in range(self._max_retries):
            try:
                resp = self._http.delete(
                    url,
                    timeout=self._timeout,
                )
                nonce = resp.headers.get("CSRF_NONCE")
                if nonce:
                    with self._lock:
                        self._http.headers["CSRF_NONCE"] = nonce

                if self._is_csrf_error(resp) and not csrf_retried:
                    logger.info("CSRF-Fehler bei DELETE %s — refreshe Nonce und wiederhole", url)
                    csrf_retried = True
                    self._refresh_csrf()
                    continue

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

    def _get_raw_stream(
        self,
        url: str,
        params: Any = None,
    ) -> httpx.Response:
        """GET mit stream=True für Datei-Downloads. Gibt die Response direkt zurück.

        Der Aufrufer muss die Response mit resp.close() schließen.
        """
        resp = self._http.stream("GET", url, params=params).__enter__()
        nonce = resp.headers.get("CSRF_NONCE")
        if nonce:
            with self._lock:
                self._http.headers["CSRF_NONCE"] = nonce
        return resp
