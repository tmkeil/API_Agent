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
from src.adapters.change_mixin import ChangeMixin
from src.adapters.documents_mixin import DocumentsMixin
from src.adapters.parts_mixin import PartsMixin
from src.adapters.search_mixin import SearchMixin
from src.adapters.versions_mixin import VersionsMixin
from src.adapters.where_used_mixin import WhereUsedMixin
from src.adapters.write_mixin import WriteMixin
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
    ChangeMixin,
    DocumentsMixin,
    VersionsMixin,
    WhereUsedMixin,
    WriteMixin,
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
