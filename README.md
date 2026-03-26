# Windchill API Explorer

**API-Layer + React-Frontend** für PTC Windchill REST Services (WRS/OData).  
Entwickelt als AI-Agent-fähige Schnittstelle zu Windchill PLM.

---

## Inhaltsverzeichnis

1. [Architektur-Überblick](#architektur-überblick)
2. [Windchill OData-Anbindung](#windchill-odata-anbindung)
3. [Startup-Prozess](#startup-prozess)
4. [Authentifizierung & Session-Management](#authentifizierung--session-management)
5. [Suche & Parallel Paging (SSE-Streaming)](#suche--parallel-paging-sse-streaming)
6. [Hintergrund-Laden (Background Search Store)](#hintergrund-laden-background-search-store)
7. [BOM-Struktur & Split-View](#bom-struktur--split-view)
8. [API Log Modul](#api-log-modul)
9. [Modularisierung & Erweiterbarkeit](#modularisierung--erweiterbarkeit)
10. [Stabilität & Fehlertoleranz](#stabilität--fehlertoleranz)
11. [Production-Readiness Assessment](#production-readiness-assessment)
12. [Dateistruktur — Backend](#dateistruktur--backend)
13. [Dateistruktur — Frontend](#dateistruktur--frontend)
14. [Deployment](#deployment)
15. [Kommandos](#kommandos)

---

## Architektur-Überblick

| Schicht | Technologie | Funktion |
|---|---|---|
| **Frontend** | React 19, Vite 6, TypeScript 5.7, TailwindCSS 3.4 | |
| **Reverse Proxy** | Nginx Alpine | `/api/*` → Backend, `/*` → Frontend |
| **Backend** | FastAPI 0.115, Python 3.11, Uvicorn | |
| **Adapter** | httpx 0.27, OData v6 | Connection Pooling (100 conn), Auto-Auth (Basic/Form) |
| **PLM** | PTC Windchill 13 | OData Services: ProdMgmt, DocMgmt, CADDocumentMgmt, ChangeMgmt |

### Frontend

React 19 Single-Page-App mit TypeScript. Drei Seiten: Login, Dashboard (Suche), Detail. Die gesamte Windchill-Kommunikation läuft über das Backend — das Frontend kennt keine OData-URLs und hat keine Credentials. Relevante Architekturentscheidungen (SSE-Streaming, Module-Level Store, Tab-basiertes Lazy-Loading) sind in den jeweiligen Backend-Abschnitten mitdokumentiert.

### 3-Schichten-Architektur (Backend)

**Routers** → **Services** → **Adapters** — jede Schicht hat eine klar abgegrenzte Verantwortung:

| Schicht | Verzeichnis | Verantwortung | Beispiel |
|---|---|---|---|
| **Routers** | `src/routers/` | HTTP-Endpunkte definieren, Request/Response validieren, Auth prüfen (`Depends(require_auth)`). Kein Business-Code. | `search.py` nimmt `GET /search?q=...` entgegen, ruft den Service auf, gibt `SearchResponse` zurück. |
| **Services** | `src/services/` | Business-Logik, DTO-Mapping, Caching, Parallelisierung. Kennen den Adapter, aber nicht HTTP. | `search_service.py` prüft den Session-Cache, ruft `client.search_entities()` auf, normalisiert mit `normalize_item()`, ranked und dedupliziert. |
| **Adapters** | `src/adapters/` | OData-Kommunikation mit Windchill. Bauen URLs, parsen JSON, handlen Paging/Retry. Kennen weder Router noch Services. | `search_mixin.py` baut den `$filter`, holt alle Seiten parallel, liefert rohe OData-Dicts zurück. |

**Warum diese Trennung?**  
Ein Router weiß nicht, wie OData funktioniert. Ein Adapter weiß nicht, ob er aus einem HTTP-Request oder einem Batch-Job aufgerufen wird. Das macht die Schichten unabhängig testbar und austauschbar — z.B. könnte ein CLI-Tool denselben Service nutzen wie der Router.

Der zentrale Adapter ist `WRSClient` — zusammengesetzt aus 8 fachlichen Mixins + einer Basis-Klasse:

```python
# windchill-api/src/adapters/wrs_client.py
class WRSClient(
    PartsMixin,       # Part-Suche, Detail
    SearchMixin,      # Multi-Entity-Suche, Streaming
    BomMixin,         # BOM-Kinder, Usage Links
    ChangeMixin,      # Affected/Resulting Items
    DocumentsMixin,   # DescribedBy, CAD, Download
    VersionsMixin,    # Versionen, Lifecycle
    WhereUsedMixin,   # Where-Used (3 Strategien)
    WriteMixin,       # Create, Update, Checkout, Checkin
    WRSClientBase,    # httpx.Client, Auth, Retry, Paging
): pass
```

Durch Pythons MRO (Method Resolution Order) können alle Mixins die HTTP-Methoden der `WRSClientBase` nutzen, ohne voneinander zu wissen.

### HTTP-Methoden-Hierarchie der WRSClientBase

Die Basis-Klasse stellt drei Ebenen von GET-Methoden bereit, die aufeinander aufbauen:

| Methode | Aufgabe | Retry | Paging |
|---|---|---|---|
| `_raw_get(url)` | Ein einzelner `httpx.Client.get()` Aufruf. Synchronisiert den `CSRF_NONCE` Header aus der Windchill-Response (nötig für spätere Write-Requests). | Nein | Nein |
| `_get(url)` | Wrapper um `_raw_get()` mit Exponential-Backoff Retry — bis zu 3 Versuche bei Timeout, Netzwerk- oder Serverfehlern (Delays: 1s → 2s → 4s, Cap 10s). | Ja (3×) | Nein |
| `_get_all_pages(url)` | OData-Paging: Ruft `_get()` auf, folgt dann sequentiell den `@odata.nextLink`-URLs bis alle Seiten geladen sind (max 200 Seiten = 5000 Items). | Ja (pro Seite) | Ja |

Jede höhere Methode nutzt die darunterliegende. Ein `_get_all_pages()`-Aufruf macht also intern N×`_get()`, und jeder `_get()` macht bis zu 3×`_raw_get()` bei Fehlern.

```python
# windchill-api/src/adapters/base.py
def _raw_get(self, url, params=None, timeout=None) -> httpx.Response:
    resp = self._http.get(url, params=params, timeout=timeout or self._timeout)
    nonce = resp.headers.get("CSRF_NONCE")
    if nonce:
        with self._lock:
            self._http.headers["CSRF_NONCE"] = nonce   # Thread-safe aktualisieren
    return resp

def _get(self, url, params=None, *, suppress_errors=False) -> Optional[httpx.Response]:
    delay = 1.0
    for attempt in range(self._max_retries):            # max 3
        try:
            resp = self._raw_get(url, params)
            if resp.status_code < 500: return resp      # 2xx/3xx/4xx → sofort zurück
        except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError):
            pass
        time.sleep(delay)
        delay = min(delay * 2, 10.0)                    # 1s → 2s → 4s
```

Die Mixins rufen fast ausschließlich `_get_all_pages()` oder `_get_json()` auf — nie direkt `_raw_get()`. Ausnahme: `SearchMixin` nutzt `_raw_get()` direkt, weil es ein eigenes Paging mit ThreadPoolExecutor implementiert und kein Retry pro einzelner Suchseite braucht.

---

## Windchill OData-Anbindung

### Verbindungsaufbau

Die OData-Base-URL wird aus `base_url` + `/servlet/odata/{version}` zusammengesetzt:

```python
# windchill-api/src/adapters/base.py — WRSClientBase.__init__()
self.base_url = base_url.rstrip("/")
self.odata_base = f"{self.base_url}/servlet/odata/{odata_version}"  # z.B. .../Windchill/servlet/odata/v6

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
```

Pro User-Session existiert eine eigene `httpx.Client`-Instanz mit eigenen Cookies/Auth. Die Windchill-Systeme sind in `config.py` konfigurierbar:

```python
# windchill-api/src/core/config.py
WINDCHILL_SYSTEMS_JSON = json.dumps({
    "prod": "https://plm-prod.neuhausen.internal/Windchill",
    "test": "https://plm-test.neuhausen.internal/Windchill",
    "dev":  "https://plm-dev.neuhausen.internal/Windchill",
})
```

### OData-Services und Entity Sets

Windchill stellt seine Daten über OData v6 Services bereit. Jeder Objekttyp lebt in einem bestimmten Service + Entity Set:

| Windchill-Typ | OData Service | Entity Set | Beispiel-URL |
|---|---|---|---|
| `WTPart` | ProdMgmt | Parts | `/servlet/odata/v6/ProdMgmt/Parts` |
| `WTDocument` | DocMgmt | Documents | `/servlet/odata/v6/DocMgmt/Documents` |
| `EPMDocument` (CAD) | CADDocumentMgmt | CADDocuments | `/servlet/odata/v6/CADDocumentMgmt/CADDocuments` |
| `WTChangeOrder2` | ChangeMgmt | ChangeNotices | `/servlet/odata/v6/ChangeMgmt/ChangeNotices` |
| `WTChangeRequest2` | ChangeMgmt | ChangeRequests | `/servlet/odata/v6/ChangeMgmt/ChangeRequests` |
| `WTChangeIssue` | ChangeMgmt | ProblemReports | `/servlet/odata/v6/ChangeMgmt/ProblemReports` |

Diese Zuordnung steckt im `SEARCHABLE_ENTITIES`-Dict des `SearchMixin`.

### Wie Daten abgerufen werden

**Einzelnes Objekt** — per ID oder Filter:

```python
# windchill-api/src/adapters/parts_mixin.py — find_part()
url = f"{self.odata_base}/ProdMgmt/Parts"
resp = self._get(url, {"$filter": f"Number eq '{safe}'"})
items = resp.json().get("value", [])   # OData liefert immer {"value": [...]}
```

```python
# Direkter Zugriff per OData-ID
url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')"
data = self._get_json(url)              # → einzelnes Dict (kein value-Array)
```

**Paging** — Windchill liefert maximal 25 Items pro Response. Mehr Daten kommen über `@odata.nextLink`.

Es gibt **zwei Paging-Varianten** in `base.py`:

| Methode | Strategie | Genutzt von |
|---|---|---|
| `_get_all_pages()` | **Sequentiell** — folgt `@odata.nextLink` Seite für Seite | Alle Mixins (BOM, Dokumente, Parts, Where-Used, Change, Versionen) |
| `_get_all_pages_parallel()` | **Parallel** — fragt mit `$count=true` die Gesamtzahl ab, berechnet alle Skiptoken-URLs vorab, ruft sie mit ThreadPoolExecutor(10) parallel ab | Aktuell nicht direkt aufgerufen (Reserve-Methode). Die Suche nutzt stattdessen ein eigenes 2-Phasen-Paging im `SearchMixin`, das ähnlich arbeitet aber pro Typ gruppiert. |

```python
# windchill-api/src/adapters/base.py — _get_all_pages() [sequentiell]
data = resp.json()
all_items = list(data.get("value", []))          # Erste 25

while "@odata.nextLink" in data and page < max_pages:
    page += 1
    resp = self._get(data["@odata.nextLink"])     # Windchill-generierte URL mit $skiptoken
    data = resp.json()
    all_items.extend(data.get("value", []))        # Nächste 25
```

```python
# windchill-api/src/adapters/base.py — _get_all_pages_parallel() [parallel]
p["$count"] = "true"                      # Erste Seite: Gesamtzahl abfragen
resp = self._get(url, p)
total_count = data.get("@odata.count")    # z.B. 150
skip_size = 25                             # Aus dem Skiptoken-Muster im nextLink extrahiert

# Alle Seiten-URLs vorab berechnen: $skiptoken=25, 50, 75, 100, 125
for pg in range(1, math.ceil(total_count / skip_size)):
    page_urls.append(f"{base_url}&$skiptoken={skip_size * pg}")

# Parallel abrufen
with ThreadPoolExecutor(max_workers=10) as pool:
    futures = {pool.submit(_fetch, pu): pu for pu in page_urls}
```

Die sequentielle Variante reicht für BOM-Abfragen (selten >100 Items). Die parallele Variante existiert als Baustein für Szenarien mit großen Ergebnismengen.

**Navigation Properties** — Beziehungen zwischen Objekten (Part → Dokumente, Part → BOM-Kinder):

```python
# Part → verknüpfte Dokumente
url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/DescribedBy"
docs = self._get_all_pages(url)

# Part → BOM Usage Links (Stückliste)
url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/Uses"
links = self._get_all_pages(url, {"$expand": "Uses"})  # $expand lädt Kind-Parts inline mit

# Usage Link → Kind-Part auflösen
url = f"{self.odata_base}/ProdMgmt/UsageLinks('{link_id}')/RoleBObject"
child = self._get_json(url)
```

### Auto-Discovery von Navigation Properties

Windchill-Versionen unterscheiden sich darin, welche Navigation Properties existieren. Das Backend probiert mehrere Varianten durch und cached die erste funktionierende:

```python
# windchill-api/src/adapters/bom_mixin.py — get_bom_children()
nav_options = ["Uses", "UsesInterface", "BOMComponents", "PartStructure"]

# Gecachte Strategie aus vorherigem Aufruf verwenden
if self._bom_nav_strategy:
    nav, use_expand = self._bom_nav_strategy
    url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/{nav}"
    result = self._get_all_pages(url, {"$expand": "Uses"} if use_expand else None)
    if result is not None:
        return result
    self._bom_nav_strategy = None   # Funktioniert nicht mehr → neu discovern

# Alle Strategien durchprobieren
for nav in nav_options:
    result = self._get_all_pages(f".../Parts('{part_id}')/{nav}", ...)
    if result is not None:
        self._bom_nav_strategy = (nav, True)
        return result
```

Dasselbe Muster bei Dokumenten (3 Quellen: `DescribedBy`, `DocMgmt`-Filter, `References`) und Usage-Link-Auflösung (3 Properties: `Uses`, `RoleBObject`, `Child`).

### OData-Feld-Normalisierung

Windchill liefert je nach Endpoint und OData-Version unterschiedliche Feldnamen für dasselbe Attribut. `odata.py` normalisiert das einmal zentral:

```python
# windchill-api/src/core/odata.py
_FIELD_ALIASES = {
    "id":       ["ID", "id"],
    "number":   ["Number", "PartNumber"],
    "name":     ["Name", "DisplayName"],
    "version":  ["Version", "VersionID"],
    "state":    ["State", "LifeCycleState"],     # State kann {Value:..., Display:...} Dict sein
    "context":  ["ContainerName", "FolderLocation"],
    # ...
}

def normalize_item(raw: dict) -> dict:
    """Alle OData-Feld-Aliase in kanonische Keys auflösen."""
    result = {}
    for canonical, aliases in _FIELD_ALIASES.items():
        value = None
        for alias in aliases:
            value = raw.get(alias)
            if value is not None:
                break
        result[canonical] = str(value) if value is not None else ""
    return result
```

**Wo wird `normalize_item` genutzt?** — In praktisch jedem Service, der OData-Daten ans Frontend weiterreicht. Beispiel aus `search_service.py`:

```python
# windchill-api/src/services/search_service.py — Suchergebnis aufbereiten
for item in raw_items:                     # item = rohes OData-Dict von Windchill
    n = normalize_item(item)               # → {"id": "...", "number": "...", "state": "Released", ...}
    if not n["id"] or n["id"] in seen_ids:
        continue
    matches.append(PartSearchResult(
        partId=n["id"],
        number=n["number"],                # Egal ob Windchill "Number" oder "PartNumber" geliefert hat
        name=n["name"],
        state=n["state"],                  # Bereits entpackt (kein {Value:..., Display:...} Dict mehr)
        ...
    ))
```

Weitere Aufrufer: `parts_service.py` (5×), `document_service.py`, `change_service.py`, `version_service.py`, `write_service.py` (5×), `bulk_service.py`, `search.py` Router (SSE `_to_search_result`). Insgesamt ~20 Aufrufstellen — ohne `normalize_item` wäre jede davon eine `.get()`-Kette mit 3+ Fallbacks.

Dadurch arbeiten Services und Frontend immer mit konsistenten Keys (`number`, `name`, `state`, ...) — unabhängig davon, welcher OData-Endpoint das Objekt geliefert hat.

---

## Startup-Prozess

### Docker Compose (`make up`)

Drei Container im Bridge-Netzwerk `wc-network`:

1. **`wc-backend`** — `uvicorn api:app --host 0.0.0.0 --port 8001`, Health-Check `GET /health` alle 30s
2. **`wc-frontend`** — `npm run dev` (Vite auf Port 5173), Volume-Mount `./src` für Live-Reload
3. **`wc-nginx`** — `envsubst` für `${BACKEND_HOST}`, Port 80 → Routing

### Backend-Initialisierung (`api.py`)

```python
# windchill-api/api.py
app = FastAPI(title="Windchill API", version="1.0.0", lifespan=lifespan)

# CORS — origins aus .env (CORS_ORIGINS)
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_credentials=True, ...)

# Timing-Header auf jeder Response
@app.middleware("http")
async def add_timing_headers(request, call_next):
    t0 = time.monotonic()
    response = await call_next(request)
    response.headers["X-Response-Time-Ms"] = str(round((time.monotonic() - t0) * 1000, 1))
    return response

# Globaler Error-Handler — WRSError → strukturierte JSON-Response (kein 500)
@app.exception_handler(WRSError)
async def wrs_error_handler(request, exc):
    return JSONResponse(status_code=exc.status_code or 502, content={"detail": str(exc)})

# 9 Router unter /api/*
app.include_router(auth_router,      prefix="/api")
app.include_router(search_router,    prefix="/api")
app.include_router(parts_router,     prefix="/api")
# ... (change, documents, versions, write, bulk, admin)
```

Es werden **keine Windchill-Verbindungen beim Start** aufgebaut. Die Verbindung entsteht genau an einer Stelle — im Login-Endpoint, wenn `WRSClient(...)` instanziiert wird:

```python
# windchill-api/src/routers/auth.py — login()
client = WRSClient(
    base_url=system_url,            # z.B. "https://plm-prod.internal/Windchill"
    username=username,
    password=password,
    odata_version=settings.WRS_ODATA_VERSION,
)
```

Der `WRSClient.__init__()` (geerbt von `WRSClientBase`) erstellt einen `httpx.Client` und ruft am Ende `self._connect()` auf. `_connect()` macht einen GET gegen `/ProdMgmt` mit Basic Auth, erkennt anhand der Antwort ob Basic oder Form Auth nötig ist, und authentifiziert sich. Erst wenn das erfolgreich war, wird die Session erstellt und der Cookie gesetzt. Schlägt `_connect()` fehl, wird der `httpx.Client` sofort geschlossen und eine `WRSError` geworfen → der Login-Endpoint gibt einen HTTP-Fehler zurück.

### Frontend-Initialisierung

`AuthProvider` ruft beim Mount `GET /api/auth/me` auf. Ist ein gültiger Session-Cookie vorhanden → User laden → Dashboard. Kein Cookie → Redirect zu `/login`.

---

## Authentifizierung & Session-Management

### Login-Flow

1. Browser sendet `POST /api/auth/login` mit `{system, username, password}`
2. Backend erstellt `WRSClient(base_url, user, pass)` → Auto-Auth-Detection:

```python
# windchill-api/src/adapters/base.py — _connect()
resp = self._http.get(f"{self.odata_base}/ProdMgmt", auth=(self._username, self._password))

if resp.status_code < 400 and "text/html" not in content_type:
    # Basic Auth akzeptiert → dauerhaft aktivieren
    self._http.auth = (self._username, self._password)
elif "j_security_check" in str(resp.url) or "text/html" in content_type:
    # Form Login nötig → POST /j_security_check mit j_username/j_password
    self._authenticate_form()
```

3. Session wird erstellt mit Per-User-Infrastruktur:

```python
# windchill-api/src/core/session.py
@dataclass
class UserSession:
    token: str                                              # secrets.token_urlsafe(32)
    client: WRSClient                                       # eigene Windchill-Verbindung
    expires_at: float                                       # Sliding Window (SESSION_TTL_SECONDS)
    part_by_id: BoundedLRUDict = field(default_factory=BoundedLRUDict)        # LRU(500)
    part_by_number: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    bom_children_by_part: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    documents_by_part: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    cad_documents_by_part: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    search_cache: BoundedLRUDict = field(default_factory=BoundedLRUDict)
    api_logs: deque = field(default_factory=lambda: deque(maxlen=500))         # Ring Buffer
```

4. Response: `Set-Cookie: wt_session=<token>; HttpOnly; SameSite=Strict`

### Token-Speicherung

| Ort | Was | Sicherheit |
|---|---|---|
| **Server-RAM** | `SessionStore._sessions[token] → UserSession` | Token nie im Client-JS sichtbar |
| **Browser** | `wt_session` Cookie (HttpOnly, SameSite=Strict) | Kein JavaScript-Zugriff möglich |
| **Windchill** | httpx.Client hält Session-Cookies (Form-Login) oder Basic Auth Header | Credentials nur im Backend |

### Drei Auth-Methoden (`require_auth`)

`require_auth` prüft, ob der **Browser-Request** eine gültige Identität hat (Session-Cookie, API Key oder Azure Token). Das ist eine In-Memory-Prüfung in der Python-Session-Store — kein Round-Trip zu Windchill.

```python
# windchill-api/src/core/auth.py
async def require_auth(request: Request) -> None:
    # 1. Session Cookie (Frontend-User) — Lookup im In-Memory SessionStore
    token = request.cookies.get(SESSION_COOKIE)
    if token and session_store.get(token):        # ← kein Windchill-Call
        return

    # 2. API Key — constant-time comparison (AI-Agent / Service-to-Service)
    api_key = request.headers.get("X-API-Key", "")
    if settings.API_KEY and api_key and hmac.compare_digest(api_key, settings.API_KEY):
        return

    # 3. Azure AD Bearer Token — JWKS auto-fetched, cached
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer ") and settings.AZURE_TENANT_ID:
        _validate_azure_token(auth_header[7:])
        return

    raise HTTPException(status_code=401, ...)
```

Danach wird der `WRSClient` aus der Session geholt (via `get_client(request)`) und macht den eigentlichen OData-Aufruf — mit dem bereits authentifizierten `httpx.Client`.

### Session-Lifecycle

- **Sliding Window**: Jeder `SessionStore.get()` verlängert `expires_at` um `SESSION_TTL_SECONDS` (Default: 3600s)
- **Reaper-Thread**: Daemon-Thread prüft alle 60s auf abgelaufene Sessions, schließt deren httpx.Clients
- **Logout**: `SessionStore.delete()` entfernt Session + schließt Client sofort

```python
# windchill-api/src/core/session.py — Reaper
def _reap() -> None:
    while True:
        time.sleep(60)
        self._evict_expired()   # Remove expired sessions, close WRSClients

t = threading.Thread(target=_reap, daemon=True, name="session-reaper")
t.start()
```

---

## Suche & Parallel Paging (SSE-Streaming)

### Das Problem

Windchill OData hat eine **feste Seitengröße von 25** — serverseitig nicht änderbar (`$top` wird ignoriert). Bei einer Suche über 6 Entitätstypen und z.B. 200 Ergebnissen pro Typ sind das 48 OData-Requests (8 Seiten × 6 Typen).

```python
# windchill-api/src/adapters/search_mixin.py
_WC_PAGE_SIZE = 25                    # Windchill liefert immer 25 Items pro Seite
_DEFAULT_SEARCH_MAX_PAGES = 200       # 200 × 25 = 5000 Items pro Typ

SEARCHABLE_ENTITIES = {
    "part":            ("ProdMgmt",        "Parts",           "WTPart"),
    "document":        ("DocMgmt",         "Documents",       "WTDocument"),
    "cad_document":    ("CADDocumentMgmt", "CADDocuments",    "EPMDocument"),
    "change_notice":   ("ChangeMgmt",      "ChangeNotices",   "WTChangeOrder2"),
    "change_request":  ("ChangeMgmt",      "ChangeRequests",  "WTChangeRequest2"),
    "problem_report":  ("ChangeMgmt",      "ProblemReports",  "WTChangeIssue"),
}
```

### 2-Phasen Parallel Paging

**Phase 1** — Erste Seite pro Typ parallel (bis zu 6 Threads, einer pro Typ):

```python
# windchill-api/src/adapters/search_mixin.py — search_entities()
with ThreadPoolExecutor(max_workers=len(targets)) as pool:
    futures = [
        pool.submit(_fetch_first, tk, svc, es, wct)
        for tk, (svc, es, wct) in targets
    ]
    for f in as_completed(futures):
        type_key, wc_type, items, next_link = f.result()
        all_items.extend(items)              # Sofort verfügbar
        # Skiptoken-Muster aus nextLink extrahieren → URLs für Phase 2 generieren
        m = _re.search(r'[\?&]\$skiptoken=(\d+)', next_link)
        skip_size = int(m.group(1))
        for pg in range(1, max_pages):
            remaining_urls.append((f"{base_url}{sep}$skiptoken={skip_size * pg}", type_key, wc_type))
```

**Phase 2** — Alle verbleibenden Seiten aller Typen in einem einzigen Pool (bis 40 Threads):

```python
# Sortierung: niedrige Skiptokens zuerst (höhere Trefferwahrscheinlichkeit)
remaining_urls.sort(key=lambda item: int(_re.search(r'\$skiptoken=(\d+)', item[0]).group(1)))

workers = min(len(remaining_urls), 40)
with ThreadPoolExecutor(max_workers=workers) as pool:
    futures = [pool.submit(_fetch_page, ru) for ru in remaining_urls]
    for f in as_completed(futures):
        all_items.extend(f.result())
```

**Warum 2 Phasen?** — Kein verschachtelter Thread-Pool (vermeidet Deadlocks), kein `$count` (spart Round-Trip pro Typ), Skiptoken-Sortierung priorisiert niedrige Offsets.

### Query-Intelligenz

Der OData-Filter wird automatisch an den Suchbegriff angepasst:

```python
# windchill-api/src/adapters/search_mixin.py
if _is_exact_number:                     # "S2200287364" → Index-Lookup (~0.5s)
    combined_filter = f"Number eq '{safe}'"
elif _has_digits:                        # "BCC08" → eq + contains
    combined_filter = f"(Number eq '{safe}' or contains(Number,'{safe}'))"
else:                                    # "Sensor" → contains auf Number + Name
    combined_filter = f"(contains(Number,'{safe}') or contains(Name,'{safe}'))"
```

### Warum SSE statt klassischem HTTP oder WebSocket?

| | Klassischer HTTP-Response | WebSocket | SSE (Server-Sent Events) |
|---|---|---|---|
| **Richtung** | Request → eine Response | Bidirektional | Server → Client (unidirektional) |
| **Erste Ergebnisse** | Erst nach Abschluss aller OData-Requests (8–15s) | Sofort möglich | Sofort möglich (~1.5s nach Phase 1) |
| **Komplexität** | Minimal | Upgrade-Handshake, Heartbeat, Reconnect, State-Mgmt | Standard-HTTP, automatischer Reconnect |
| **Nginx** | Out-of-box | Erfordert `proxy_set_header Upgrade` Konfiguration | `X-Accel-Buffering: no` reicht |
| **Abbruch** | Client kann `AbortController` nutzen | `close()` | `AbortController` / Disconnect-Detection |

Für die Suche ist SSE ideal: Der Server pusht Ergebnis-Batches, der Client zeigt sie sofort an. Bidirektionale Kommunikation (WebSocket) wäre Overkill — der Client sendet nach dem initialen Request keine weiteren Daten. Ein klassischer HTTP-Response müsste auf alle 6 Typen × N Seiten warten, bevor der User das erste Ergebnis sieht.

### SSE-Streaming (Server → Browser)

Backend: Sync-Generator (Thread) → `asyncio.Queue` → Async-Generator → `StreamingResponse`

```python
# windchill-api/src/routers/search.py — SSE-Endpoint
async def _generate():
    queue: asyncio.Queue[list[dict] | None] = asyncio.Queue()
    cancelled = threading.Event()
    loop = asyncio.get_event_loop()

    def _producer():
        for batch in client.search_entities_stream(q, cancelled=cancelled):
            if cancelled.is_set():
                break
            results = [_to_search_result(item) for item in batch]
            loop.call_soon_threadsafe(queue.put_nowait, results)
        loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

    thread = threading.Thread(target=_producer, daemon=True)
    thread.start()

    while True:
        # Disconnect-Detection alle 0.5s
        if await request.is_disconnected():
            cancelled.set()    # → Producer bricht OData-Requests ab
            return
        batch = await asyncio.wait_for(queue.get(), timeout=0.5)
        if batch is None: break
        yield f"data: {json.dumps(batch)}\n\n"
```

Frontend: Kein `EventSource` — stattdessen `fetch()` + `ReadableStream` (mehr Kontrolle über AbortController):

```typescript
// windchill-frontend/src/api/client.ts — searchPartsStream()
export function searchPartsStream(q, onBatch, onDone, onError): AbortController {
  const controller = new AbortController()

  fetch(`${BASE}/search/stream?${params}`, {
    credentials: 'include',
    signal: controller.signal,
    headers: { Accept: 'text/event-stream' },
  }).then(async (resp) => {
    const reader = resp.body?.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      // SSE-Events extrahieren (getrennt durch \n\n)
      const segments = buffer.split('\n\n')
      buffer = segments.pop() || ''
      for (const seg of segments) parseEvent(seg)
    }
  })
  return controller
}
```

### Timing-Beispiele

| Suchbegriff | Ergebnis | OData-Requests | Dauer |
|---|---|---|---|
| `S2200287364` (exakte Nummer) | 6 Seiten (1×6 Typen) | 6 | ~1.5s |
| `BES*` (Wildcard) | ~30 Seiten (5×6 Typen) | ~30 | ~4–8s |
| `Sensor` (Text) | ~60 Seiten (10×6 Typen) | ~60 | ~8–15s |

Erste Ergebnisse sind nach Phase 1 (~1.5s) im Browser sichtbar. Weitere Ergebnisse trudeln im Hintergrund ein.

---

## Hintergrund-Laden (Background Search Store)

Wenn der User ein Suchergebnis anklickt und zur Detailseite navigiert, wird `DashboardPage` unmounted. Damit der SSE-Stream weiterläuft und die Ergebnisse nicht verloren gehen, liegt der Search-State **außerhalb von React** auf Modul-Ebene:

```typescript
// windchill-frontend/src/pages/DashboardPage.tsx — Module-Level (vor der Komponente)
let _store: SearchStore = { query: '', results: [], searching: false, done: false, error: '', durationMs: 0 }
let _abortCtrl: AbortController | null = null
const _listeners = new Set<() => void>()

function startSearch(query: string, types?: string[]) {
  _abortCtrl?.abort()   // Vorherige Suche abbrechen
  _store = { query, results: [], searching: true, done: false, error: '', durationMs: 0 }
  _notify()             // Alle Listener benachrichtigen

  const ctrl = searchPartsStream(
    query,
    (batch) => {       // onBatch — wird auch aufgerufen, wenn DashboardPage unmounted ist
      _store = { ..._store, results: [..._store.results, ...batch] }
      _notify()
    },
    (info) => { _store = { ..._store, searching: false, done: true, durationMs: info.durationMs }; _notify() },
    (msg) =>  { _store = { ..._store, searching: false, done: true, error: msg }; _notify() },
    { types },
  )
  _abortCtrl = ctrl
}
```

**Angebunden via `useSyncExternalStore`** (React 18+ API):

```typescript
// windchill-frontend/src/pages/DashboardPage.tsx — in der Komponente
const searchState = useSyncExternalStore(subscribeStore, getStoreSnapshot)
const { results, searching, done: searchDone, error } = searchState
```

### Ablauf

1. User sucht `BES*` → `startSearch("BES*")` → SSE-Stream startet
2. User klickt ein Ergebnis → `navigate('/detail/part/S2200287364')` → DashboardPage unmounts
3. **SSE-Stream läuft weiter** — `_store` wird im Hintergrund befüllt
4. User klickt "Zurück zur Suche" → DashboardPage re-mounted → `useSyncExternalStore` liest `_store` → alle Ergebnisse (inkl. während der Abwesenheit geladener) sind sofort da
5. Query wird aus URL wiederhergestellt (`?q=BES*`) → kein Re-Fetch nötig, wenn `_store.query === urlQuery`

### URL-State Sync

```typescript
// Query in URL persistieren → Back-Button funktioniert
const handleSearch = useCallback((query: string) => {
  setSearchParams(query ? { q: query } : {}, { replace: true })
  startSearch(query, activeTypes.length > 0 ? activeTypes : undefined)
}, [activeTypes, setSearchParams])
```

---

## BOM-Struktur & Split-View

### Lazy-Loading BOM-Baum

Die BOM wird erst auf expliziten Klick geladen. Pro Level:

1. `GET /api/bom/root?partNumber=...` → Root-Node
2. User klickt Aufklapppfeil → `GET /api/bom/children?partId=OR:...`
3. Backend parallelisiert mit `ThreadPoolExecutor(16)`: Kinder auflösen (Usage Links → Child Parts), Dokumente laden (DescribedBy), CAD-Dokumente laden
4. Kinder erscheinen eingerückt. Rekursiv bei nächstem Klick.

### Windchill-Style Split View

Beim Klick auf einen BOM-Eintrag teilt sich die Ansicht (55% BOM-Tabelle / 45% Detail-Panel):

- **Linke Seite**: BOM-Tabelle, selektierter Eintrag blau markiert
- **Rechte Seite**: `BomDetailPanel` mit 3 Sub-Tabs (Übersicht, Attribute, Dokumente)
- **↗-Icon**: Öffnet vollständige Detailseite
- **X-Button**: Schließt Panel (BOM nimmt 100% Breite ein)

### 5 BOM-Ansichten

Konfigurierbar über `GET /api/bom/views` (`bom_views.py`):

| Ansicht | Spalten | Fokus |
|---|---|---|
| Standard | Nummer, Name, Version, Status, Menge, Einheit | Grunddaten |
| Erweitert | + Line Number, SAP Cr., Sign, Org-ID | Produktionsdetails |
| SAP | SAP-spezifische Attribute (BALSAPNAME etc.) | ERP-Integration |
| Rohmaterial | Gewicht, Maße, Materialtyp | Engineering |
| Alle Felder | ~20 Spalten | Diagnose |

---

## API Log Modul

Bei Session-Erstellung werden **httpx Event-Hooks** am Client registriert — jeder OData-Request wird automatisch protokolliert:

```python
# windchill-api/src/core/session.py — instrument_client_requests()
def _on_request(request):
    request.extensions["_log_start"] = time.perf_counter()

def _on_response(response):
    start = response.request.extensions.get("_log_start", 0)
    duration_ms = int((time.perf_counter() - start) * 1000)
    log_session_event(session, method=str(response.request.method),
                      url=str(response.request.url),
                      status=response.status_code, duration_ms=duration_ms, source="windchill")

hooks = http_client.event_hooks
hooks["request"].append(_on_request)
hooks["response"].append(_on_response)
```

Das `ApiLogPanel` (Frontend, eingebettet in `Layout.tsx`) pollt `GET /api/logs?limit=120` alle 2.5s wenn geöffnet und zeigt die Einträge terminal-artig an (dark, monospace, farbkodiert: grün=OK, rot=4xx/5xx, gelb=Cache).

Pro Session maximal 500 Einträge (`deque(maxlen=500)`).

---

## Modularisierung & Erweiterbarkeit

### Backend erweitern

**Neuer Windchill-Bereich** (z.B. Promotions):
1. Neues Mixin erstellen: `src/adapters/promotions_mixin.py`
2. In `WRSClient` einhängen (eine Zeile):
   ```python
   class WRSClient(PromotionsMixin, PartsMixin, ..., WRSClientBase): pass
   ```
3. Service erstellen: `src/services/promotion_service.py`
4. Router erstellen: `src/routers/promotions.py`
5. In `api.py` registrieren: `app.include_router(promotions_router, prefix="/api")`

**Neuer Suchtyp** (z.B. PromotionNotice):
1. In `SEARCHABLE_ENTITIES` eintragen (eine Zeile):
   ```python
   "promotion": ("ChangeMgmt", "PromotionNotices", "WTPromotionNotice"),
   ```

### Frontend erweitern

**Neuer Detail-Tab**:
1. Neue Datei in `src/components/detail/` erstellen
2. In `DetailPage.tsx` als `TabKey` + `TABS_BY_TYPE`-Eintrag registrieren

**Neuer Windchill-Typ**:
1. `TYPE_LABELS` in `labels.ts` erweitern
2. `SUBTYPE_BADGE_STYLES` in `labels.ts` erweitern (Farbe für Badge)

### Router-Isolation

Jeder Router ist ein eigenständiges Modul mit eigenem Prefix:

| Router | Prefix | Endpoints |
|---|---|---|
| `auth.py` | `/auth` | `/systems`, `/login`, `/logout`, `/me` |
| `search.py` | `/search`, `/objects` | `/stream` (SSE), `/advanced`, `/{type_key}/{code}` |
| `parts.py` | `/parts`, `/bom` | `/{code}`, `/root`, `/children`, `/views` |
| `change.py` | `/changes` | `/{type_key}/{code}/affected`, `/resulting` |
| `documents.py` | `/documents` | `/{type_key}/{code}/referencing-parts`, `/files` |
| `versions.py` | `/objects` | `/{type_key}/{code}/versions`, `/lifecycle` |
| `write.py` | `/write` | `/create`, `/{type_key}/{code}/attributes`, `/state` |
| `bulk.py` | `/bulk` | `/details` |
| `admin.py` | `/logs`, `/export` | `/diagnose/bom-fields`, `/cache/*` |

---

## Stabilität & Fehlertoleranz

### Backend

**Exponential Backoff Retry** (`base.py`):

```python
# windchill-api/src/adapters/base.py — _get()
delay = 1.0
for attempt in range(self._max_retries):        # max 3
    try:
        resp = self._raw_get(url, params)
        if resp.status_code < 500: return resp
    except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError):
        pass
    if attempt < self._max_retries - 1:
        time.sleep(delay)
        delay = min(delay * 2, 10.0)            # 1s → 2s → 4s (cap 10s)
```

**Bounded Caches** — Speicher bleibt begrenzt:

```python
# windchill-api/src/core/session.py
class BoundedLRUDict(OrderedDict):
    """OrderedDict mit max size — evicts oldest entry bei overflow."""
    def __setitem__(self, key, value):
        if key in self: self.move_to_end(key)
        super().__setitem__(key, value)
        if len(self) > self._maxsize: self.popitem(last=False)   # _maxsize = 500
```

**CSRF Nonce Tracking** — automatisch aus jeder Windchill-Response extrahiert:

```python
# windchill-api/src/adapters/base.py — _raw_get()
nonce = resp.headers.get("CSRF_NONCE")
if nonce:
    with self._lock:
        self._http.headers["CSRF_NONCE"] = nonce
```

Weitere Mechanismen:
- **Session Reaper**: Daemon-Thread entfernt abgelaufene Sessions alle 60s → kein Memory Leak
- **Connection Pooling**: `httpx.Limits(max_connections=100, max_keepalive_connections=40)`
- **SSE Disconnect-Detection**: `request.is_disconnected()` alle 0.5s → `cancelled.set()` → OData-Requests werden gestoppt
- **Globaler WRSError Handler**: Jeder unbehandelte `WRSError` → strukturierte JSON-Response

### Frontend

- **useSyncExternalStore**: Module-Level Store überlebt Navigation → kein Datenverlust
- **URL-State Sync**: Query in URL (`?q=...`) → Back-Button stellt Suche wieder her
- **AbortController**: Jeder Tab mit eigenem AbortController → Cleanup bei Unmount
- **ErrorBoundary**: React Error Boundary → Fehlerseite statt White Screen
- **Per-Tab Fetching**: Tabs laden unabhängig → kein Wasserfall-Loading

---

## Production-Readiness Assessment

### Produktionsreif

| Bereich | Bewertung |
|---|---|
| **Modularisierung** | Exzellent — Mixin-Pattern, Feature-isolierte Router/Services/Tabs |
| **Fehlerbehandlung** | Solide — Retry mit Backoff, Error Boundaries, strukturierte Fehlermeldungen |
| **Sicherheit** | Gut — HttpOnly+SameSite Cookies, CSRF-Nonce, HMAC für API-Key, kein Token in JS |
| **Performance** | Gut — 2-Phasen Parallel Paging, Connection Pooling, Multi-Layer Caching (LRU+TTL) |
| **Memory Management** | Gut — Bounded LRU(500), TTL(60s/1000), deque(500), Session Reaper |
| **Erweiterbarkeit** | Exzellent — Neue Mixins/Router/Tabs ohne bestehenden Code zu ändern |

### Verbesserungspotential

| Bereich | Empfehlung |
|---|---|
| **Tests** | Unit-Tests für Services, Integration-Tests für OData-Adapter |
| **Logging** | Strukturiertes JSON-Logging + Log-Aggregation (ELK/Loki) |
| **Monitoring** | Prometheus Metrics (`/metrics`), Grafana Dashboard |
| **Rate Limiting** | Nginx rate limiting oder FastAPI-Middleware |
| **Secrets** | Azure Key Vault statt `.env` |
| **Shared State** | Redis für Caches bei Multi-Instance Deployment |
| **HTTPS** | TLS-Termination in Nginx/Loadbalancer |
| **CI/CD** | GitHub Actions: Lint, Type-Check, Test, Build, Deploy |

**Fazit**: Für Single-Instance-Betrieb produktionsbereit. Für High-Availability müssten Caches externalisiert (Redis) und Sessions persistent gespeichert werden.

---

## Dateistruktur — Backend

```
windchill-api/
├── api.py                          # FastAPI Entry Point — CORS, Middleware, Router-Registrierung
├── requirements.txt                # FastAPI, httpx, pydantic, PyJWT
├── Dockerfile                      # Python 3.11-slim, Port 8001
│
└── src/
    ├── core/
    │   ├── config.py               # Pydantic Settings (.env), WINDCHILL_SYSTEMS Dict
    │   ├── auth.py                 # require_auth — Cookie / API Key / Azure AD
    │   ├── session.py              # SessionStore, UserSession, LRU Caches, API Log, Reaper
    │   ├── cache.py                # TTLCache — Thread-safe (60s TTL, 1000 max)
    │   ├── dependencies.py         # get_session(), get_client() — Request → Session → Client
    │   ├── odata.py                # normalize_item(), WcType, match_score()
    │   └── bom_views.py            # 5 BOM-View Konfigurationen (Spalten → OData-Felder)
    │
    ├── models/
    │   └── dto.py                  # ~30 Pydantic DTOs (PartDetail, BomTreeNode, ObjectDetail, ...)
    │
    ├── adapters/
    │   ├── base.py                 # WRSClientBase — httpx.Client, Auth, Retry, Paging
    │   ├── parts_mixin.py          # find_part, search_parts, get_soft_attributes (IBAs)
    │   ├── search_mixin.py         # 6 Entitätstypen, 2-Phasen Parallel Paging, SSE-Stream
    │   ├── bom_mixin.py            # get_bom_children — Auto-Discovery des Nav-Property
    │   ├── documents_mixin.py      # 3 Quellen: DescribedBy, DocMgmt, References
    │   ├── where_used_mixin.py     # 3 Strategien: Action, UsedBy, UsageLinks
    │   ├── change_mixin.py         # Affected/Resulting Items
    │   ├── versions_mixin.py       # Versionen + Lifecycle (3 Nav-Strategien + Fallback)
    │   ├── write_mixin.py          # Create, Update, Set State, Checkout, Checkin
    │   └── wrs_client.py           # WRSClient = alle Mixins via MRO + Service-Account Singleton
    │
    ├── services/
    │   ├── parts_service.py        # BOM-Kinder (ThreadPoolExecutor(16)), Docs, Where-Used
    │   ├── search_service.py       # search_parts (+ Session Cache + Ranking), get_object_detail
    │   ├── change_service.py       # Affected/Resulting → ChangeItem DTOs
    │   ├── document_service.py     # Referencing Parts, File Info, Download
    │   ├── version_service.py      # Versions + Lifecycle (Pseudo-History Fallback)
    │   ├── write_service.py        # Create, Update, State, Checkout, Checkin → WriteResponse
    │   ├── bulk_service.py         # Parallel Bulk Details (ThreadPoolExecutor(8))
    │   └── admin_service.py        # BOM Export, Benchmark
    │
    └── routers/
        ├── auth.py                 # /auth/systems, /auth/login, /auth/logout, /auth/me
        ├── search.py               # /search, /search/stream (SSE), /search/advanced, /objects
        ├── parts.py                # /parts/{code}, /bom/root, /bom/children, /bom/views
        ├── change.py               # /changes/{type_key}/{code}/affected, /resulting
        ├── documents.py            # /documents/{type_key}/{code}/referencing-parts, /files
        ├── versions.py             # /objects/{type_key}/{code}/versions, /lifecycle
        ├── write.py                # /write/create, /write/{type_key}/{code}/attributes, etc.
        ├── bulk.py                 # /bulk/details
        └── admin.py                # /logs, /export, /diagnose/bom-fields, /cache/*
```

---

## Dateistruktur — Frontend

```
windchill-frontend/
├── index.html                      # HTML Entry Point
├── package.json                    # React 19, React Router 7, Vite 6, TailwindCSS 3.4
├── vite.config.ts                  # Proxy /api → Backend, HMR, Port 5173
├── tsconfig.json                   # ES2020, strict, react-jsx
├── Dockerfile                      # Multi-Stage: Dev (Vite) / Prod (Nginx)
│
└── src/
    ├── main.tsx                    # ReactDOM.createRoot → <App>
    ├── App.tsx                     # BrowserRouter, AuthProvider, ProtectedRoute, Routes
    ├── index.css                   # Tailwind Directives
    │
    ├── api/
    │   ├── client.ts               # request<T>(), searchPartsStream() (SSE via ReadableStream),
    │   │                           # Auth, Search, BOM, Detail, Write, Admin Funktionen
    │   └── types.ts                # ~40 TypeScript Interfaces
    │
    ├── contexts/
    │   └── AuthContext.tsx          # getMe() beim Mount, Cookie-basiert (credentials: 'include')
    │
    ├── pages/
    │   ├── LoginPage.tsx           # System-Auswahl + Login Form
    │   ├── DashboardPage.tsx       # Module-Level External Store + SSE + URL-State Sync
    │   └── DetailPage.tsx          # TABS_BY_TYPE-Konfiguration pro Windchill-Typ
    │
    ├── components/
    │   ├── Layout.tsx              # Header (System, User, Logout) + ApiLogPanel
    │   ├── SearchBar.tsx           # Suchfeld mit Enter-Handler + Loading-Spinner
    │   ├── ErrorBoundary.tsx       # React Error Boundary
    │   ├── ApiLogPanel.tsx         # Terminal-Display, pollt alle 2.5s wenn offen
    │   ├── AdvancedSearchPanel.tsx  # Feldbasierte Suche (Typ, Kontext, Felder)
    │   ├── MultiSelect.tsx         # Wiederverwendbare Multiselect-Dropdown
    │   ├── OccurrencesPanel.tsx    # "Wo kommt dieses Part vor?"
    │   ├── BomTreeNode.tsx         # Rekursive BOM-Zeile, Lazy-Loading, Selection-Support
    │   │
    │   └── detail/
    │       ├── DetailHeader.tsx    # Typ-Badge, Nummer, Name, Version, Status
    │       ├── DetailsTab.tsx      # Kerndaten
    │       ├── AttributesTab.tsx   # Alle OData-Attribute (filterbar)
    │       ├── StructureTab.tsx    # BOM-Tabelle + Split-View + 5 Ansichten
    │       ├── BomDetailPanel.tsx  # Split-View Panel (Übersicht, Attribute, Dokumente)
    │       ├── AllDocumentsTab.tsx  # DescribedBy + CAD gruppiert
    │       ├── DocumentsTab.tsx    # Wrapper für DocumentListTab
    │       ├── CadTab.tsx          # Wrapper für DocumentListTab
    │       ├── DocumentListTab.tsx # Generische Dokumentenliste
    │       ├── WhereUsedTab.tsx    # Where-Used Tabelle
    │       ├── OccurrencesTab.tsx  # Vorkommen eines Parts
    │       ├── ChangeItemsTab.tsx  # Affected/Resulting Items
    │       ├── ReferencingPartsTab.tsx  # Referenzierende Parts
    │       ├── FileInfoTab.tsx     # Dateianhänge
    │       ├── VersionsTab.tsx     # Versionshistorie
    │       ├── LifecycleTab.tsx    # Lifecycle-Timeline
    │       └── WriteActionsPanel.tsx  # Checkout, Checkin, Set State
    │
    └── utils/
        └── labels.ts               # TYPE_LABELS, SUBTYPE_BADGE_STYLES (20+ Typen),
                                    # subtypeBadgeStyle(), typeLabel(), formatDate()
```

---

## Deployment

### Docker Compose

```yaml
services:
  backend:    # FastAPI auf Port 8001, Health Check alle 30s
  frontend:   # Vite Dev Server auf Port 5173, Volume-Mount für Live-Reload
  nginx:      # Reverse Proxy auf Port 80 — /api/* → Backend, /* → Frontend
```

### Umgebungsvariablen (Backend `.env`)

| Variable | Beschreibung | Default |
|---|---|---|
| `CORS_ORIGINS` | Erlaubte CORS Origins | — |
| `API_KEY` | Shared Secret für AI-Agent Auth | — |
| `SESSION_TTL_SECONDS` | Session-Timeout | 3600 |
| `WRS_ODATA_VERSION` | OData Version | v6 |
| `LOG_TIMING` | Response-Timing in Konsole | false |
| `AZURE_TENANT_ID` / `AZURE_CLIENT_ID` | Azure AD JWT-Validation | — |

---

## Kommandos

```bash
# Docker
make up               # Alle Container starten (lokal, mit override)
make up-prod          # Produktion (nur docker-compose.yml)
make down             # Container stoppen
make build            # Neu bauen + starten
make logs             # Logs aller Container
make logs-be          # Nur Backend-Logs

# Lokal (ohne Docker)
make install          # Dependencies installieren
make dev              # Backend + Frontend parallel

# API Docs → http://localhost:8001/docs (Swagger) / /redoc
```
