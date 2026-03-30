# Windchill API Explorer — Präsentations-Leitfaden

> Geschätzte Dauer: ~25 Minuten. 8 Stationen. Jede Station hat: **was zeigen**, **was sagen**, **welches File aufmachen**.

---

## Station 1: Architektur in 60 Sekunden

### Zeigen

**File:** `windchill-api/src/adapters/wrs_client.py` — Zeile 55–66

```python
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

### Sagen

> Das Backend hat drei Schichten: **Routers**, **Services**, **Adapters**.
> Dadurch kann jede Schicht unabhängig getestet, erweitert und ausgetauscht werden. Das macht Änderungen billiger, Fehler schneller findbar und neue Features schneller umsetzbar.
>
> - **Routers** (`src/routers/`) — definieren die HTTP-Endpunkte. Nehmen Requests an, validieren, rufen den Service auf. Kein Business-Code.
> - **Services** (`src/services/`) — Business-Logik. Caching, Parallelisierung, DTO-Mapping. Rufen den Adapter auf.
> - **Adapters** (`src/adapters/`) — reden mit Windchill über OData. Bauen URLs, parsen JSON, handlen Paging und Retry. Wissen nichts von HTTP.
>
> Der zentrale Adapter ist dieser `WRSClient` hier. Er ist aus 8 Mixins zusammengesetzt — jede Zeile ist ein fachlicher Bereich. Durch Pythons MRO (Method Resolution Order) können alle Mixins die HTTP-Methoden der Basis-Klasse nutzen, ohne voneinander zu wissen. Neuer Windchill-Bereich? Neues Mixin erstellen.
>
> Das Frontend ist eine React 19 Single-Page-App mit TypeScript. Drei Seiten: Login, Dashboard mit Suche, Detailseite. Die gesamte Windchill-Kommunikation läuft über das Backend — das Frontend kennt keine OData-URLs.

---

## Station 2: Login — Wie entsteht eine Windchill-Verbindung?

### Zeigen: 4 Files in Reihenfolge

**1. File:** `windchill-frontend/src/pages/LoginPage.tsx` — Zeile 34–38

```tsx
async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    await login(system, username, password)
```

### Sagen

> Der User wählt ein Windchill-System (prod/test/dev), gibt Username und Passwort ein. Das Frontend schickt einen POST an `/api/auth/login`.

---

**2. File:** `windchill-api/src/routers/auth.py` — Zeile 36–75

```python
async def login(body: LoginRequest, request: Request):
    system_url = WINDCHILL_SYSTEMS[system_key]

    client = WRSClient(
        base_url=system_url,
        username=username,
        password=password,
    )

    session = session_store.create(
        system_key=system_key,
        system_url=system_url,
        username=username,
        client=client,
    )

    response.set_cookie(SESSION_COOKIE, session.token, httponly=True, samesite="strict")
```

### Sagen

> Hier im Router passiert die eigentliche Verbindung: `WRSClient(...)` wird erstellt. Der Konstruktor ruft intern `_connect()` auf — das ist der nächste Schritt.
>
> Wichtig: Der **Router** erstellt nur den Client und die Session. Die **Auth-Logik** steckt im **Adapter** (`_connect()`). Das ist die Schichten-Trennung in Aktion.

---

**3. File:** `windchill-api/src/adapters/base.py` — Zeile 106–185

```python
def _connect(self) -> None:
    # Schritt 1: Test-GET mit Basic Auth
    resp = self._http.get(f"{self.odata_base}/ProdMgmt", auth=(username, password))

    # Schritt 2a: Basic Auth akzeptiert
    if resp.status_code < 400 and "text/html" not in content_type:
        self._http.auth = (self._username, self._password)
        return

    # Schritt 2b: Redirect zur Login-Seite → Form Auth nötig
    if "j_security_check" in str(resp.url) or "text/html" in content_type:
        self._authenticate_form()     # POST /j_security_check mit j_username/j_password
        self._verify_authenticated()  # Gegencheck: Kommt jetzt JSON statt HTML?
        return
```

### Sagen

> Das ist die Auto-Auth-Detection. Verschiedene Windchill-Systeme nutzen verschiedene Auth-Verfahren. Manche akzeptieren Basic Auth direkt, manche redirecten auf ein Login-Formular (`j_security_check` — Java EE Standard).
>
> Der Code probiert Basic Auth und schaut sich die Antwort an. Kommt JSON zurück → Basic Auth funktioniert. Kommt eine HTML-Login-Seite → Form Auth nötig.
>
> **Wichtig:** Diese Authentifizierung passiert **einmalig** beim Login. Danach hält der `httpx.Client` die Credentials (Basic Auth Header oder Session-Cookie). Alle weiteren OData-Requests nutzen die gespeicherte Session — kein erneuter Login pro Request.

---

**4. File:** `windchill-api/src/core/session.py` — Zeile 39–55

```python
@dataclass
class UserSession:
    token: str                        # secrets.token_urlsafe(32)
    client: WRSClient                 # eigene Windchill-Verbindung
    expires_at: float                 # Sliding Window
    part_by_id: BoundedLRUDict        # LRU(500) — Pro-User-Cache
    part_by_number: BoundedLRUDict
    bom_children_by_part: BoundedLRUDict
    documents_by_part: BoundedLRUDict
    search_cache: BoundedLRUDict
    api_logs: deque                   # Ring Buffer (maxlen=500)
```

### Sagen

> Jeder eingeloggte User bekommt eine eigene Session mit:
> - Eigenem `httpx.Client` (eigene Cookies, eigene Windchill-Verbindung)
> - 6 LRU-Caches (je max 500 Einträge) — damit wiederholte Abfragen nicht nochmal zu Windchill müssen
> - Ein API-Log (Ring Buffer) — jeder OData-Request wird automatisch protokolliert
>
> Der Session-Token ist ein HttpOnly-Cookie — JavaScript im Browser hat keinen Zugriff. Ein Reaper-Thread räumt alle 60 Sekunden abgelaufene Sessions auf und schließt deren HTTP-Clients.

---

## Station 3: Suche — Frontend

### Zeigen

**File:** `windchill-frontend/src/pages/DashboardPage.tsx` — Zeile 33–70

```tsx
// ── Module-Level (außerhalb der React-Komponente) ──
let _store: SearchStore = { query: '', results: [], searching: false, ... }
let _abortCtrl: AbortController | null = null

function startSearch(query: string, types?: string[]) {
  _abortCtrl?.abort()                    // Vorherige Suche abbrechen
  _store = { query, results: [], searching: true, ... }

  const ctrl = searchPartsStream(
    query,
    (batch) => {                         // onBatch — wird bei jedem SSE-Event aufgerufen
      _store = { ..._store, results: [..._store.results, ...batch] }
      _notify()
    },
    (info) => { ... },                   // onDone
    (msg) => { ... },                    // onError
  )
}

// ── In der React-Komponente ──
const searchState = useSyncExternalStore(subscribeStore, getStoreSnapshot)
```

### Sagen

> Das Besondere hier: Der Search-State lebt **außerhalb** von React auf Modul-Ebene. Warum?
>
> Wenn der User ein Suchergebnis anklickt, navigiert er zur Detailseite — diese Komponente wird unmounted. Aber der SSE-Stream läuft im Hintergrund weiter und befüllt `_store`. Kommt der User zurück, sind alle Ergebnisse (inkl. der währenddessen nachgeladenen) sofort da.
>
> `useSyncExternalStore` ist die React 18+ API dafür — die Komponente subscribt sich auf den externen Store und re-rendert bei Änderungen.

---

**File:** `windchill-frontend/src/api/client.ts` — Zeile 107–135

```typescript
export function searchPartsStream(q, onBatch, onDone, onError): AbortController {
  const controller = new AbortController()

  fetch(`${BASE}/search/stream?${params}`, {
    credentials: 'include',
    signal: controller.signal,
    headers: { Accept: 'text/event-stream' },
  }).then(async (resp) => {
    const reader = resp.body?.getReader()
    // SSE-Events parsen: Jedes \n\n-getrennte Segment ist ein Event
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      // ... parseEvent() → onBatch() oder onDone()
    }
  })
  return controller   // Aufrufer kann .abort() zum Abbrechen
}
```

### Sagen

> Kein `EventSource` — stattdessen `fetch()` mit `ReadableStream`. Das gibt uns einen `AbortController`: Die Suche kann jederzeit abgebrochen werden, und der Server wird darüber informiert.
>
> Jedes SSE-Event enthält ein JSON-Array von Suchergebnissen. Die kommen batchweise rein — der User sieht die ersten Treffer nach ~1.5 Sekunden, der Rest trudelt im Hintergrund nach.

---

## Station 4: Suche — Backend (Die 3 Optimierungen)

**Das ist der wichtigste Teil der Präsentation.**

### Optimierung 1: Query-Intelligenz

**File:** `windchill-api/src/adapters/search_mixin.py` — Zeile 142–155

```python
_has_digits = any(c.isdigit() for c in query)
_is_exact_number = _has_digits and len(query) >= 5 and not _has_wildcards

if _is_exact_number:                                               # "S2200287364"
    combined_filter = f"Number eq '{safe}'"                        # → Index-Lookup (~0.5s)
elif _has_digits:                                                  # "BCC08"
    combined_filter = f"(Number eq '{safe}' or contains(Number,'{safe}'))"
else:                                                              # "Sensor"
    combined_filter = f"(Number eq '{safe}' or contains(Number,'{safe}') or contains(Name,'{safe}'))"
```

### Sagen

> Windchill OData hat keine Volltextsuche. Der Code analysiert den Suchbegriff und wählt den effizientesten Filter:
>
> - Eine exakte Teilenummer wie `S2200287364` → `Number eq '...'` — nutzt den Index, ~0.5 Sekunden.
> - Eine Teilnummer wie `BCC08` → eq + contains — etwas breiter.
> - Ein Text wie `Sensor` → contains auf Number UND Name — am breitesten, aber findet alles.
>
> Das passiert im **Adapter** — der Service und Router wissen davon nichts.

---

### Optimierung 2: 2-Phasen Parallel Paging

**File:** `windchill-api/src/adapters/search_mixin.py` — Zeile 162 (Phase 1) + Zeile 230 (Phase 2)

### Sagen

> Windchill liefert **immer nur 25 Items pro Seite** — serverseitig nicht konfigurierbar, `$top` wird ignoriert. Bei einer Suche über 6 Objekttypen (Parts, Dokumente, CAD, Change Notices, Change Requests, Problem Reports) und z.B. 200 Treffern pro Typ sind das **48 OData-Requests** (8 Seiten × 6 Typen).
>
> **Phase 1:** Erste Seite jedes Typs parallel abrufen (6 Threads, einer pro Typ). Dauert ~1.5 Sekunden. Ergebnisse werden **sofort** als SSE-Event zum Browser gestreamt.
>
> **Phase 2:** Alle verbleibenden Seiten aller Typen in einem **einzigen Pool mit bis zu 40 Threads**. Niedrige Skiptokens zuerst — da stehen die relevantesten Treffer.
>
> Warum zwei Phasen? Kein verschachtelter Thread-Pool (vermeidet Deadlocks), und der User sieht sofort Ergebnisse statt 15 Sekunden auf eine leere Seite zu starren.

---

### Optimierung 3: SSE statt klassischem HTTP

**File:** `windchill-api/src/routers/search.py` — Zeile 74–178

```python
async def search_stream(q, ...):
    async def _generate():
        queue: asyncio.Queue = asyncio.Queue()
        cancelled = threading.Event()

        def _producer():                            # Sync-Thread
            for batch in client.search_entities_stream(q, cancelled=cancelled):
                if cancelled.is_set(): break
                results = [_to_search_result(item) for item in batch]
                loop.call_soon_threadsafe(queue.put_nowait, results)

        thread = threading.Thread(target=_producer, daemon=True)
        thread.start()

        while True:
            if await request.is_disconnected():     # Alle 0.5s prüfen
                cancelled.set()                     # → OData-Requests stoppen
                return
            batch = await asyncio.wait_for(queue.get(), timeout=0.5)
            if batch is None: break
            yield f"data: {json.dumps(batch)}\n\n"  # SSE-Event

    return StreamingResponse(_generate(), media_type="text/event-stream")
```

### Sagen

> Warum SSE statt normalem HTTP-Response? Ein normaler Response müsste auf **alle** 48 OData-Requests warten, bevor der User etwas sieht. SSE pusht Batches sobald sie fertig sind.
>
> Warum kein WebSocket? Wäre Overkill — der Client sendet nach dem initialen Request keine Daten mehr. SSE ist unidirektional (Server → Client), läuft über Standard-HTTP, braucht keine spezielle Nginx-Config.
>
> Hier sieht man auch die **Disconnect-Detection** (Zeile mit `is_disconnected`): Alle 0.5 Sekunden prüft der Server, ob der Browser noch da ist. Wenn nicht, setzt er `cancelled` — und die OData-Requests im Producer-Thread werden sofort gestoppt. Das spart unnötigen Traffic zu Windchill.
>
> Die Bridge zwischen dem synchronen Thread (OData) und dem async-Generator (FastAPI/SSE) läuft über eine `asyncio.Queue`.

---

## Station 5: Detailseite

### Zeigen

**File:** `windchill-api/src/core/odata.py` — Zeile 20–70

```python
_FIELD_ALIASES = {
    "id":       ["ID", "id"],
    "number":   ["Number", "PartNumber"],
    "name":     ["Name", "DisplayName"],
    "version":  ["Version", "VersionID"],
    "state":    ["State", "LifeCycleState"],     # State kann auch {Value:..., Display:...} sein
    ...
}

def normalize_item(raw: dict) -> dict:
    result = {}
    for canonical, aliases in _FIELD_ALIASES.items():
        for alias in aliases:
            value = raw.get(alias)
            if value is not None: break
        result[canonical] = str(value) if value is not None else ""
    return result
```

### Sagen

> Windchill liefert je nach OData-Endpoint **unterschiedliche Feldnamen** für dasselbe Attribut. `Number` vs. `PartNumber`, `State` als String vs. als verschachteltes Dict mit `Value` und `Display`.
>
> `normalize_item()` löst das einmal zentral auf. Wird an **~20 Stellen** aufgerufen — in parts_service, search_service, document_service, change_service, version_service, write_service. Ohne diese Funktion hätten wir überall 3-fach-Fallback-Ketten.
>
> Das ist auch ein gutes Beispiel für die Schichten-Trennung: `normalize_item()` wohnt in `core/odata.py` — eine Utility, die von Services benutzt wird, aber weder Router noch Adapter kennt.

---

**File:** `windchill-frontend/src/pages/DetailPage.tsx` — Zeile 31–50

```tsx
const TABS_BY_TYPE: Record<string, TabDef[]> = {
  part:            [details, attributes, structure, allDocs, whereUsed, occurrences, changes, versions, lifecycle, write],
  document:        [details, attributes, referencingParts, fileInfo, versions, lifecycle],
  cad_document:    [details, attributes, referencingParts, fileInfo, versions, lifecycle],
  change_notice:   [details, attributes, changeItems, versions, lifecycle],
  // ...
}
```

### Sagen

> Die Tabs sind pro Windchill-Objekttyp konfiguriert. Ein WTPart hat BOM-Struktur und Where-Used, ein WTDocument hat Referencing Parts und File Info.
>
> Jeder Tab fetcht unabhängig — kein Wasserfall-Loading. Der User sieht sofort die Grunddaten, die Tabs laden ihre Daten erst wenn sie angeklickt werden.

---

## Station 6: Stabilität

**Drei Stellen schnell nacheinander zeigen:**

### 6a: Retry mit Backoff

**File:** `windchill-api/src/adapters/base.py` — Zeile 273–310

```python
def _get(self, url, params=None, *, suppress_errors=False):
    delay = 1.0
    for attempt in range(self._max_retries):        # max 3
        try:
            resp = self._raw_get(url, params)
            if resp.status_code < 500: return resp
        except (httpx.TimeoutException, httpx.NetworkError, httpx.ConnectError):
            pass
        time.sleep(delay)
        delay = min(delay * 2, 10.0)               # 1s → 2s → 4s (Cap 10s)
```

### Sagen

> Jede `_get()`-Anfrage hat automatisch Exponential Backoff Retry. 3 Versuche, Delays verdoppeln sich. Fängt Timeouts, Netzwerkfehler und 5xx-Serverfehler. Das ist in der Basis-Klasse — alle Mixins profitieren davon automatisch.

---

### 6b: Automatisches API-Logging

**File:** `windchill-api/src/core/session.py` — Zeile 82–110

### Sagen

> Bei Session-Erstellung werden httpx Event-Hooks registriert. Jeder OData-Request, den dieser Client macht, wird automatisch geloggt: Methode, URL, Status-Code, Dauer in Millisekunden. Sichtbar im API-Log-Panel im Frontend — ein Terminal-ähnliches Dark-Panel, farbkodiert (grün=OK, rot=Fehler).
>
> Kein manuelles Logging nötig — jeder Request, egal aus welchem Mixin, wird erfasst.

---

### 6c: Bounded Caches + Session Reaper

**File:** `windchill-api/src/core/session.py` — Zeile 21–55

### Sagen

> Alle Caches sind **bounded** — maximal 500 Einträge, LRU-Eviction. Kein unbegrenztes Wachstum. Der Reaper-Thread prüft alle 60 Sekunden auf abgelaufene Sessions und schließt deren HTTP-Clients. Dadurch kein Memory Leak, auch wenn User ihren Tab einfach schließen.

---

## Station 7: BOM Export — Drei Modi

### Zeigen

**File:** `windchill-frontend/src/components/detail/StructureTab.tsx` — Export-Dropdown im BOM-Tab

> Im BOM-Tab gibt es ein Dropdown "⬇ Export ▾" mit drei Optionen.

**File:** `windchill-api/src/services/admin_service.py` — Zeile 236–290

```python
def build_export(root_tree, part_number, system_url, username, client=None):
    """Build BOM export data and write to JSON file."""
    mf_cache: dict[str, OrderedDict] = {}
    bom_tree = frontend_tree_to_export(root_tree, client=client, mf_cache=mf_cache)
    stats = count_tree_stats(bom_tree)
    export_data = OrderedDict([
        ("export_info", OrderedDict([...])),
        ("bom", bom_tree),
    ])
```

**File:** `windchill-api/src/services/admin_service.py` — Zeile 74–140 (Made-From)

```python
def _resolve_made_from(part_attrs, client=None, mf_cache=None):
    mf_number = raw["made_from_number"]
    cached = mf_cache.get(mf_number)          # Cache-Hit?
    if cached is not None: return cached
    mf_raw = client.find_object("part", mf_number)  # Windchill-Lookup
    # → Ergebnis: type, number, name, version, state, part_attributes, raw_dimensions
```

### Sagen

> Drei Exportmodi:
>
> **Geladenen Baum** — exportiert nur was der User im Browser aufgeklappt hat. Die Daten gehen vom Frontend zum Backend, werden dort mit allen Attributen angereichert und als JSON-Datei geschrieben.
>
> **Vollständiger Export** — der Server traversiert die komplette BOM rekursiv. Ein `part_cache` erkennt Duplikate, damit Parts die mehrfach verbaut sind nur einmal von Windchill geholt werden.
>
> **Erweiterter Export** — zusätzlich zum Design-BOM werden über `BALDOWNSTREAM` die Manufacturing-Äquivalente gefunden. Jede Manufacturing-Part bekommt ihren eigenen BOM-Baum. Gathering-Parts (Suffix=GATH) werden erfasst aber nicht expandiert.
>
> In jedem Modus werden **Made-From-Beziehungen vollständig aufgelöst**: nicht nur die Nummer, sondern Name, Version, Status, alle Attribute. Ein `mf_cache` verhindert doppelte Lookups.

---

## Station 8: Schreiboperationen — Aktionen-Tab

### Zeigen

**File:** `windchill-api/src/adapters/write_mixin.py` — Zeile 35–45

```python
_WRITABLE_ENTITIES: dict[str, tuple[str, str]] = {
    "part":            ("ProdMgmt",        "Parts"),
    "document":        ("DocMgmt",         "Documents"),
    "cad_document":    ("CADDocumentMgmt", "CADDocuments"),
    "change_notice":   ("ChangeMgmt",      "ChangeNotices"),
    "change_request":  ("ChangeMgmt",      "ChangeRequests"),
    "problem_report":  ("ChangeMgmt",      "ProblemReports"),
}
```

**File:** `windchill-api/src/adapters/write_mixin.py` — Zeile 130–180 (Lifecycle-Status)

```python
# Strategie 1: OData Action (Windchill 12+)
action_url = f".../{entity_set}('{obj_id}')/PTC.{service}.SetLifeCycleState"
resp = self._post(action_url, json_body={"State": target_state})

# Strategie 2: Fallback — generischer PATCH
resp = self._patch(patch_url, json_body={"State": target_state})
```

**File:** `windchill-frontend/src/components/detail/WriteActionsPanel.tsx`

> Auf der Detailseite jedes Objekts gibt es einen "Aktionen"-Tab mit 4 Buttons: Auschecken, Einchecken, Status ändern, Attribut ändern.

### Sagen

> 5 Schreiboperationen auf 6 Objekttypen — alles über einen einzigen Router `/write`.
>
> Jede Write-Operation braucht einen **CSRF_NONCE**, den Windchill bei jedem Response als Header mitschickt. Der wird im `base.py` automatisch ge-tracked und bei der nächsten Anfrage mitgesendet.
>
> Der Lifecycle-Status-Wechsel hat einen **2-Strategien-Ansatz**: Zuerst OData Action (das ist der offizielle Weg ab Windchill 12). Falls das fehlschlägt, Fallback auf einen direkten PATCH. Damit funktioniert es auch auf älteren Windchill-Versionen.
>
> Im Frontend gibt es den "Aktionen"-Tab: Auschecken, Einchecken, Status ändern, Attribut ändern — mit inline Mini-Formularen und Erfolgs-/Fehlermeldungen.

---

## Abschluss der Haupt-Stationen (30 Sekunden)

### Sagen

> **Zusammengefasst:**
>
> Login verbindet sich einmal zu Windchill — erkennt automatisch Basic oder Form Auth. Pro User eine eigene Verbindung mit Caches.
>
> Die Suche parallelisiert über 6 Objekttypen mit 2-Phasen-Paging und bis zu 40 Threads. SSE streamt die Ergebnisse sofort zum Browser.
>
> BOM-Daten lassen sich in drei Modi als JSON exportieren — inklusive vollständiger Made-From-Auflösung. Der Extended Export traversiert automatisch Design → Manufacturing.
>
> Schreibende Operationen nutzen CSRF_NONCE und einen 2-Strategien-Ansatz für Lifecycle-Änderungen.
>
> Alles ist nach Router/Service/Adapter getrennt. Ein neuer Windchill-Bereich = neues Mixin + Service + Router. Kein bestehender Code wird angefasst.

---

## Spickzettel: File-Reihenfolge

| # | File | Zeilen | Thema |
|---|---|---|---|
| 1 | `windchill-api/src/adapters/wrs_client.py` | 55–66 | WRSClient = 8 Mixins |
| 2 | `windchill-frontend/src/pages/LoginPage.tsx` | 34–38 | Frontend Login |
| 3 | `windchill-api/src/routers/auth.py` | 36–75 | WRSClient erstellen, Session + Cookie |
| 4 | `windchill-api/src/adapters/base.py` | 106–185 | `_connect()` Auto-Auth |
| 5 | `windchill-api/src/core/session.py` | 39–55 | UserSession mit Caches |
| 6 | `windchill-frontend/src/pages/DashboardPage.tsx` | 33–70 | Module-Level Store |
| 7 | `windchill-frontend/src/api/client.ts` | 107–135 | SSE fetch + ReadableStream |
| 8 | `windchill-api/src/adapters/search_mixin.py` | 142–155 | Query-Intelligenz |
| 9 | `windchill-api/src/adapters/search_mixin.py` | 162–260 | 2-Phasen Parallel Paging |
| 10 | `windchill-api/src/routers/search.py` | 74–178 | SSE + Disconnect-Detection |
| 11 | `windchill-api/src/core/odata.py` | 20–70 | normalize_item() |
| 12 | `windchill-frontend/src/pages/DetailPage.tsx` | 31–50 | TABS_BY_TYPE |
| 13 | `windchill-api/src/services/admin_service.py` | 74–150 | Made-From-Auflösung + mf_cache |
| 14 | `windchill-api/src/services/admin_service.py` | 610–700 | Extended Export (Design → Mfg) |
| 15 | `windchill-api/src/adapters/write_mixin.py` | 130–180 | Lifecycle 2-Strategien |
| 16 | `windchill-frontend/src/components/detail/WriteActionsPanel.tsx` | 1–50 | Aktionen-Tab |
| 17 | `windchill-api/src/adapters/base.py` | 273–310 | Retry + Backoff |
| 18 | `windchill-api/src/core/session.py` | 82–110, 21–55 | Logging + Caches |

---

## Bonus-Beispiel 1: Login — Von der Eingabemaske bis zur Windchill-Session

> Dieses Beispiel zeigt den kompletten Login-Flow: Vom Formular im Browser über die Authentifizierung gegen Windchill bis zum Session-Cookie.

### Schritt 1: Frontend — User gibt Credentials ein

**File:** `windchill-frontend/src/pages/LoginPage.tsx`

```tsx
export default function LoginPage() {
  const { login, error } = useAuth()             // ← login() kommt aus dem AuthContext
  const [system, setSystem] = useState('dev')     // ← Dropdown: dev/test/prod
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    await login(system, username, password)        // ← Ruft AuthContext.login() auf
  }

  return (
    <form onSubmit={handleSubmit}>
      <select value={system} ...>                  {/* Windchill-System wählen */}
      <input value={username} .../>                {/* Benutzername */}
      <input type="password" value={password} .../>{/* Passwort */}
      <button type="submit">Anmelden</button>
    </form>
  )
}
```

Die Systeme (dev/test/prod) werden beim Laden der Seite von `GET /api/auth/systems` geholt. Fallback-Werte sind hardcoded, falls das Backend nicht erreichbar ist.

### Schritt 2: AuthContext — Globaler Auth-State

**File:** `windchill-frontend/src/contexts/AuthContext.tsx`

```tsx
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null)

  // Beim App-Start: Prüfen ob schon ein gültiger Session-Cookie existiert
  useEffect(() => {
    getMe()                                        // GET /api/auth/me
      .then(setUser)                               // → Cookie gültig → User laden
      .catch(() => setUser(null))                  // → Kein Cookie → Login zeigen
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback(async (system, username, password) => {
    const info = await apiLogin(system, username, password)   // ← POST /api/auth/login
    setUser(info)                                              // → React-State → Dashboard
  }, [])
}
```

`AuthProvider` umschließt die gesamte App. Sobald `setUser(info)` gesetzt wird, rendert React die `ProtectedRoute` → `DashboardPage` statt `LoginPage`.

### Schritt 3: API-Client — HTTP-Request ans Backend

**File:** `windchill-frontend/src/api/client.ts`

```typescript
export async function login(system: string, username: string, password: string): Promise<UserInfo> {
  return request<UserInfo>(`${BASE}/auth/login`, {
    method: 'POST',
    body: JSON.stringify({ system, username, password }),
    //     ↑ Credentials als JSON im Body, NICHT als URL-Parameter
  })
}
```

→ Browser sendet: `POST /api/auth/login` mit Body `{"system":"dev","username":"tobke","password":"..."}`

### Schritt 4: Router — Empfängt Login, erstellt WRSClient

**File:** `windchill-api/src/routers/auth.py`

```python
@router.post("/login")
async def login(body: LoginRequest, request: Request):
    system_url = WINDCHILL_SYSTEMS[system_key]     # z.B. "https://plm-dev.internal/Windchill"

    # ↓↓↓ HIER passiert die Windchill-Verbindung ↓↓↓
    client = WRSClient(
        base_url=system_url,
        username=username,
        password=password,
    )
    # Wenn wir hier ankommen, ist die Verbindung erfolgreich.
    # Bei falschem Passwort wirft WRSClient eine WRSError → der User sieht "Login fehlgeschlagen"

    session = session_store.create(                # ← Session im RAM speichern
        system_key=system_key,
        system_url=system_url,
        username=username,
        client=client,                             # ← Der authentifizierte WRSClient wird gespeichert
    )

    response = JSONResponse({"ok": True, "username": username, ...})
    response.set_cookie(                           # ← Session-Token als Cookie
        SESSION_COOKIE, session.token,
        httponly=True,                             # JavaScript kann den Cookie nicht lesen
        samesite="strict",                         # Nur Same-Origin Requests senden ihn
    )
    return response
```

Der Router delegiert **keine** Auth-Logik — er ruft nur `WRSClient(...)` auf. Die gesamte Windchill-Kommunikation passiert im Adapter (nächster Schritt).

### Schritt 5: Adapter — `__init__` → `_connect()` → Windchill-Auth

**File:** `windchill-api/src/adapters/base.py`

```python
class WRSClientBase:
    def __init__(self, base_url, username, password, ...):
        self.odata_base = f"{base_url}/servlet/odata/v6"

        self._http = httpx.Client(                 # ← Ein HTTP-Client pro User
            verify=verify_tls,
            follow_redirects=True,
            headers={"Accept": "application/json"},
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=40),
        )

        self._connect()                            # ← Sofort verbinden + authentifizieren
```

```python
    def _connect(self) -> None:
        # Schritt 1: Test-GET mit Basic Auth
        resp = self._http.get(
            f"{self.odata_base}/ProdMgmt",
            auth=(self._username, self._password),  # ← Einmaliger expliziter Auth-Header
        )

        # Schritt 2a: Basic Auth hat funktioniert → dauerhaft aktivieren
        if resp.status_code < 400 and "text/html" not in content_type:
            self._http.auth = (self._username, self._password)
            return                                  # ✓ Fertig — alle folgenden Requests nutzen Basic Auth

        # Schritt 2b: Server hat auf Login-Seite umgeleitet → Form Auth nötig
        if "j_security_check" in str(resp.url) or "text/html" in content_type:
            self._authenticate_form()               # POST /j_security_check mit j_username/j_password
            self._verify_authenticated()            # Gegencheck: JSON statt HTML?
            return                                  # ✓ Fertig — httpx.Client hat jetzt Session-Cookie

        # Schritt 2c: Weder Basic noch Form → Fehler
        raise WRSError("Authentifizierung fehlgeschlagen", 401)
```

**Warum Auto-Detection?** Verschiedene Windchill-Instanzen (dev/test/prod) können unterschiedliche Auth-Verfahren nutzen. Der Code probiert Basic Auth und schaut sich die Antwort an: JSON = Basic klappt, HTML = Form Login nötig. Das passiert **einmalig** — danach hält `self._http` die Credentials.

### Schritt 6: Session — Der WRSClient wird gespeichert

**File:** `windchill-api/src/core/session.py`

```python
class SessionStore:
    def create(self, system_key, system_url, username, client) -> UserSession:
        token = secrets.token_urlsafe(32)          # ← Zufälliger 43-Zeichen-String
        session = UserSession(
            token=token,
            client=client,                         # ← Der authentifizierte WRSClient
            expires_at=time.time() + 3600,          # ← 1 Stunde gültig (Sliding Window)
            part_by_id=BoundedLRUDict(),            # ← Eigener Cache pro User
            part_by_number=BoundedLRUDict(),
            bom_children_by_part=BoundedLRUDict(),
            api_logs=deque(maxlen=500),             # ← Eigenes API-Log pro User
        )
        instrument_client_requests(session)         # ← httpx Event-Hooks für Auto-Logging
        self._sessions[token] = session             # ← Im RAM speichern
        return session
```

### Zusammenfassung: Der Rückweg

```
Windchill  ←  _connect(): "Auth OK" (200 + JSON oder Session-Cookie)
Adapter    →  WRSClient-Instanz mit authentifiziertem httpx.Client
Router     →  session_store.create() → Session mit Token
              response.set_cookie("wt_session", token)
Browser    →  Cookie gespeichert, AuthContext.setUser(info) → Dashboard wird angezeigt
```

### Was passiert ab jetzt bei jedem weiteren Request?

```
Browser: GET /api/parts/S123 + Cookie "wt_session=abc123..."
  → require_auth:  session_store.get("abc123...") → Session gefunden ✓ (RAM-Lookup, kein Windchill-Call)
  → get_client():  session.client → der gespeicherte WRSClient mit der bereits authentifizierten Verbindung
  → Adapter:       self._http.get("...ProdMgmt/Parts?...") → nutzt die bestehende Session, kein erneuter Login
```

---

## Bonus-Beispiel 2: Ein Request von Klick bis Windchill (Occurrences)

> Dieses Beispiel zeigt den kompletten Datenfluss durch alle Schichten — vom Button-Klick im Browser bis zur OData-Antwort von Windchill und zurück.

### Kontext: Wie React entscheidet, was angezeigt wird

React Router in `App.tsx` matched die URL gegen die Route-Definitionen:

```tsx
// windchill-frontend/src/App.tsx
<Route path="/" element={<DashboardPage />} />
<Route path="/detail/:typeKey/:code" element={<DetailPage />} />
```

Wenn die URL von `/` auf `/detail/part/S2200287364` wechselt, wird `DashboardPage` **unmounted** (aus dem DOM entfernt, React-State weg) und `DetailPage` gemounted. Immer nur eine Page ist aktiv. Innerhalb der `DetailPage` werden Tabs wie `OccurrencesPanel` als Kinder gerendert.

### Schritt 1: Frontend — User klickt "Vorkommen suchen"

**File:** `windchill-frontend/src/components/OccurrencesPanel.tsx`

```tsx
export default function OccurrencesPanel() {
  const handleSubmit = useCallback(async (e: FormEvent) => {
    const data = await getOccurrences(code)    // ← HTTP-Request ans Backend
    setResult(data)                            // ← React-State → UI-Update
  }, [code])

  return (
    <form onSubmit={handleSubmit}>
      <input value={code} onChange={...} />
      <button type="submit">Vorkommen suchen</button>
    </form>
  )
}
```

### Schritt 2: Frontend — API-Client baut die URL

**File:** `windchill-frontend/src/api/client.ts`

```typescript
export async function getOccurrences(code: string): Promise<OccurrencesResponse> {
  return request<OccurrencesResponse>(`${BASE}/parts/${encodeURIComponent(code)}/occurrences`)
  //     ↑ fetch() mit credentials:'include' → Session-Cookie wird mitgeschickt
}
```

→ Browser sendet: `GET /api/parts/S2200287364/occurrences` + Cookie `wt_session=abc123...`

### Schritt 3: Router — Empfängt den Request, prüft Auth

**File:** `windchill-api/src/routers/parts.py`

```python
@router.get("/parts/{code}/occurrences", response_model=OccurrencesResponse)
def get_occurrences(
    code: str,
    request: Request,
    _: None = Depends(require_auth),       # ← Prüft: Hat der Cookie eine gültige Session?
):
    client = get_client(request)           # ← Holt den WRSClient aus der Session
    return parts_service.get_part_occurrences(client, code)   # ← Ruft den Service auf
```

`require_auth` schaut im In-Memory `session_store`, ob der Token `abc123...` existiert und nicht abgelaufen ist. **Kein Windchill-Call** — reine RAM-Prüfung. `get_client()` holt dann den `WRSClient` aus derselben Session — der hat seit dem Login eine authentifizierte `httpx.Client`-Instanz.

### Schritt 4: Service — Business-Logik und DTO-Mapping

**File:** `windchill-api/src/services/parts_service.py`

```python
def get_part_occurrences(client: WRSClient, code: str) -> OccurrencesResponse:
    raw = client.search_parts(code, limit=500)     # ← Ruft den Adapter auf
    occurrences = []
    for item in raw:
        p = _map_part(item)                        # ← Rohes OData-Dict → sauberes DTO
        occurrences.append(PartOccurrence(
            partId=p.partId, number=p.number, name=p.name, ...
        ))
    return OccurrencesResponse(code=code, totalFound=len(occurrences), occurrences=occurrences)
```

Der Service weiß nichts über HTTP oder OData-URLs. Er bekommt einen `client`, ruft eine Methode darauf auf, und mapped das Ergebnis auf Pydantic DTOs.

### Schritt 5: Adapter — OData-Requests an Windchill

**File:** `windchill-api/src/adapters/parts_mixin.py`

```python
def search_parts(self, query: str, limit: int = 25) -> list[dict]:
    url = f"{self.odata_base}/ProdMgmt/Parts"       # ← OData-URL zusammenbauen
    strategies = [
        {"$filter": f"Number eq '{safe}'"},          # Exakt (schnell, Index)
        {"$filter": f"contains(Number,'{safe}')"},   # Nummer enthält
        {"$filter": f"contains(Name,'{safe}')"},     # Name enthält
    ]
    for params in strategies:
        items = self._get_all_pages(url, params)     # ← GET an Windchill (mit Retry + Paging)
        for item in items:
            collected[extract_id(item)] = item
    return list(collected.values())[:limit]
```

`_get_all_pages()` nutzt den **bereits authentifizierten** `httpx.Client` (seit Login). Es wird **keine neue Verbindung** aufgebaut — der Client hat die Session-Cookies/Basic-Auth schon gespeichert. Bei >25 Ergebnissen folgt er automatisch den `@odata.nextLink`-URLs.

### Zusammenfassung: Der Rückweg

```
Windchill  →  [rohe OData-Dicts]
Adapter    →  list[dict]              an den Service
Service    →  OccurrencesResponse     (Pydantic DTO) an den Router
Router     →  JSON Response           an den Browser
React      →  setResult(data)         → UI-Update
```

Jede Schicht transformiert die Daten in ihr Format: Windchill liefert OData-JSON, der Adapter gibt rohe Dicts, der Service mappt auf typisierte DTOs, der Router serialisiert zu JSON, React rendert HTML.

---

## Falls Fragen kommen

| Frage | Kurze Antwort |
|---|---|
| "Wird bei jedem Request gegen Windchill authentifiziert?" | Nein — einmalig beim Login. Danach hält der `httpx.Client` die Session. `require_auth` prüft nur den Browser-Cookie im In-Memory Store. |
| "Warum kein WebSocket?" | Unidirektional reicht. SSE ist einfacher (Standard-HTTP, kein Upgrade-Handshake, keine Heartbeats). |
| "Wie erweiterbar ist das?" | Neuer Windchill-Bereich = 1 Mixin + 1 Service + 1 Router + 1 Zeile in `wrs_client.py`. Kein bestehender Code wird geändert. |
| "Warum Python und nicht Node?" | httpx gibt uns Connection-Pooling, echtes Threading (ThreadPoolExecutor), synchrone OData-Calls in Parallel — passt besser als Node's Event-Loop für CPU-armes I/O-Batching. |
| "Wie sicher sind die Credentials?" | Windchill-Passwort nur im Backend-RAM (httpx.Client). Session-Token als HttpOnly+SameSite Cookie — kein JS-Zugriff. API-Key via HMAC constant-time compare. |
| "Wie funktioniert der CSRF-Schutz bei Writes?" | Windchill schickt bei jedem Response einen `CSRF_NONCE`-Header. Der wird in `base.py` automatisch gespeichert und bei der nächsten Write-Anfrage mitgesendet. |
| "Warum zwei Strategien für Lifecycle-State?" | OData Action ist der offizielle Weg (Windchill 12+). Der PATCH-Fallback funktioniert auch auf älteren Versionen. Das Backend probiert automatisch beides. |





Initial commit: Windchill PLM API Explorer

Full-stack application for exploring and navigating Windchill PLM data
via OData v6.

Backend:  FastAPI 0.115 / Python 3.11 — 3-layer architecture
          (Routers → Services → Adapters), SSE streaming, session mgmt
Frontend: React 19 / Vite 6 / TypeScript 5.7 / TailwindCSS
          Split-view with search, detail page, BOM navigation
Infra:    Docker Compose (backend + frontend + nginx reverse proxy)
Docs:     README.md (architecture deep-dive), PRAESENTATION.md (walkthrough)