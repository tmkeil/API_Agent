# Windchill API

API-Layer über **PTC Windchill REST Services**.  
Kapselt die WRS-Komplexität und liefert normalisierte Produktdaten.

---

## Der Nutzen

### Zeitersparnis

Viele Datenzugriffe erfordern im UI lange Klickserien mit mehrminütigen Ladezeiten:

| Aktion | UI (manuell) | API |
|---|---|---|
| Part-Stammdaten laden | ~1 Min. (Suche → öffnen → Attribute laden) | ~200–500 ms |
| BOM mit 200 Teilen anzeigen | ~3–5 Min. (Structure-Tab → Expand All) | ~1–3 s |
| Code in 30 Produktfamilien suchen | Nahezu unmöglich manuell | ~2–10 s |

### Use Case: „Wo kommt Code XABC vor?"

Ein Anwendungsfall: ein Teilcode taucht in mehreren Produktfamilien auf unterschiedlichen Hierarchieebenen auf. Die API aggregiert alle Vorkommen, extrahiert Kontext (Produktfamilie, Revision, Freigabestatus) und liefert das normalisiert als JSON:

```json
{
  "code": "XABC",
  "total_found": 3,
  "occurrences": [
    { "number": "XABC", "name": "Stecker Typ A", "revision": "B", "state": "Released" },
    { "number": "XABC", "name": "Stecker Typ A (Variant)", "revision": "A", "state": "In Work" }
  ],
  "timing": { "total_ms": 312, "wrs_ms": 287, "from_cache": false }
}
```

---

## Architektur

Die **Windchill API** läuft als eigenständiger FastAPI-Prozess (Port 8001) und sitzt zwischen den Clients und PTC Windchill.

**Clients** (SSO-App, ERP, BI, Scripts) authentifizieren sich per `Authorization: Bearer <Azure AD Token>` oder `X-API-Key` Header — je nach Konfiguration (siehe unten).

Die API selbst enthält Timing-Middleware, CORS, einen TTL-In-Memory-Cache (Standard 60 s) sowie einen OData-Adapter mit automatischem Retry und CSRF-Nonce-Verwaltung. Alle Routen liegen unter `/api/parts/*`.

**Authentifizierung gegen Windchill:** Die API authentifiziert sich intern per **HTTP Basic Auth** mit einem dedizierten Service-Account gegen die WRS OData-Schnittstelle.

---

## Credentials: `WRS_USERNAME` / `WRS_PASSWORD`

Das sind die normalen **Windchill-Login-Daten** — dasselbe Konto, mit dem man sich im Browser bei Windchill anmeldet.

**Zum Entwickeln und Testen:** Eigene Zugangsdaten verwenden. Solange der Account in Windchill Read-Zugriff auf die benötigten Parts hat, funktioniert alles.

**Im Produktivbetrieb:** IT bitten, einen dedizierten Service Account anzulegen (z. B. `svc_api_read`) mit minimalen ACL-Rechten (`Read`, ggf. `Download`). So lässt sich der Zugriff der API unabhängig von einzelnen Personen verwalten und der Account kann bei Bedarf gesperrt werden ohne andere zu beeinflussen.

Credentials in `.env` eintragen:
```
WRS_USERNAME=vorname.nachname      # oder später: svc_api_read
WRS_PASSWORD=dein-windchill-passwort
```

`.env` niemals committen — steht bereits in `.gitignore`.

---

## API Key: `API_KEY`

Den **API Key erfindest du selbst** — er ist kein Windchill-Konto und kommt von keinem externen System. Es ist einfach ein geheimer String, der schützt, dass Unbefugte deine API aufrufen.

Einen sicheren Zufalls-Key erzeugen:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
# Beispiel-Output: a3f1c8e2d94b7065f2a1e8b3c0d4f91e7a2b5c6d8e9f0a1b2c3d4e5f6a7b8c9
```

Diesen String dann in `.env` eintragen:
```
API_KEY=a3f1c8e2d94b7065f2a1e8b3c0d4f91e7a2b5c6d8e9f0a1b2c3d4e5f6a7b8c9
```

Beim Aufruf der API dann im Header mitsenden:
```bash
curl -H "X-API-Key: a3f1c8e2..." "http://localhost:8001/api/parts/XABC"
```

---

## Endpunkte

| Method | Pfad | Beschreibung |
|---|---|---|
| `GET` | `/api/parts/{code}` | Stammdaten eines Parts (Name, Revision, Status) |
| `GET` | `/api/parts/{code}/occurrences` | Alle Vorkommen des Codes in Windchill |
| `GET` | `/api/parts/{code}/bom` | Mehrstufige Stückliste (`?levels=max` oder `?levels=3`) |
| `GET` | `/api/parts/{code}/where-used` | Einsatzverwendung: in welchen Parent-Parts ist dieser Code verbaut? |
| `GET` | `/api/benchmark?code={code}` | Live-Performance-Messung vs. geschätzter UI-Zeit |
| `GET` | `/api/cache/stats` | Cache-Füllstand und TTL |
| `DELETE` | `/api/cache` | Cache invalidieren (frische Daten aus Windchill) |
| `GET` | `/health` | Health-Check (kein API-Key) |
| `GET` | `/docs` | Swagger UI |

---

## Performance-Messung für Stakeholder

Jede API-Antwort enthält ein `timing`-Objekt:

```json
"timing": {
  "total_ms": 1240,
  "wrs_ms": 1180,
  "cache_hits": 0,
  "from_cache": false
}
```

`wrs_ms` ist die Zeit, die in WRS-Calls verbracht wurde. Der Delta (`total_ms - wrs_ms`) ist der Overhead dieser API (Mapping, Aggregation) — typischerweise < 20 ms.

`GET /api/benchmark?code=XABC` führt einen Live-Benchmark aus und vergleicht die API-Laufzeit mit der geschätzten manuellen UI-Zeit:

```json
{
  "results": [
    {
      "endpoint": "GET /parts/XABC/bom",
      "description": "Vollständige BOM laden (243 Komponenten)",
      "api_ms": 1340,
      "estimated_ui_minutes": 1.2,
      "speedup_factor": 54,
      "note": "UI: Structure-Tab → Expand All → Warten ≈ 1.2 Min. für 243 Teile."
    }
  ],
  "summary": "Die API ist bis zu 54× schneller als die manuelle Windchill-UI für 'XABC'."
}
```

Der `X-Response-Time-Ms` Response-Header enthält zusätzlich die Gesamtzeit pro Request — direkt in Monitoring-Tools verwertbar.

---

## Cache

Häufig abgefragte Parts und BOMs werden im In-Memory-TTL-Cache gehalten (Standard: 60 Sekunden).
Wird dieselbe BOM zweimal innerhalb von 60 s abgefragt, beantwortet die API die zweite Anfrage sofort ohne WRS-Call.

Für Multi-Prozess-Deployments sollte der Cache auf Redis migriert werden.

---

## Quick Start (lokal)

```bash
cd windchill-api

# Virtual Environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux/Mac

# Dependencies
pip install -r requirements.txt

# Konfiguration
cp .env.example .env
# .env bearbeiten: WRS_BASE_URL, WRS_USERNAME, WRS_PASSWORD, API_KEY setzen

# Starten
python api.py
# → http://localhost:8001/docs
```

**Erster Test:**
```bash
curl -H "X-API-Key: <api-key>" \
  "http://localhost:8001/api/parts/XABC"
```

---

## Anbindung an bestehende Systeme

### Bestehende interne Web-App

Das Backend der Hauptanwendung ruft die Windchill-API intern auf und reicht die Daten normalisiert ans Frontend weiter. Die API ist ein Service, der über den API-Key aufgerufen wird.

```
Nutzer (Browser)
    │  SSO
    ▼
Frontend
    │  /api/windchill/parts/XABC
    ▼
Backend Hauptanwendung
    │  Azure AD Bearer Token oder API-Key
    ▼
Windchill API
    │
    ▼
Windchill (WRS/OData)
```

### SAP oder anderes ERP

ERP-Systeme können die API per HTTP-Call direkt ansprechen.
SAP z. B. über ABAP `cl_http_client` oder über SAP Integration Suite / SAP API Management als zwischengeschalteten Layer.

### BI / Reporting (Power BI, Excel, Python)

Power BI kann REST-APIs als Web-Datenquelle einbinden. In Python-Skripten (z. B. Jupyter Notebook) können `requests` oder `httpx` genutzt werden:

```python
# Python
import requests

resp = requests.get(
    "http://windchill-api.company.internal/api/parts/XABC/bom",
    headers={"X-API-Key": "..."}
)
bom = resp.json()
```

### MES / Fertigungssysteme

Fertigungssysteme könnten automatisiert die aktuelle freigegebene Stückliste (`state: Released`) aus Windchill abrufen.

---

## Nächste Schritte

### Where-Used-Pfad anpassen

`GET /parts/{code}/where-used` ist implementiert und nutzt `PTC.ProdMgmt.GetWhereUsed`. Falls Windchill mit HTTP 404 antwortet, ist der Pfad in der installierten WRS-Version anders — das Response-Feld `note` enthält dann einen Hinweis. Im Windchill UI unter `Browse → Customization → Documentation → OData REST APIs` die korrekte Action oder Navigation Property unter `ProdMgmt` nachschlagen und in `src/adapters/wrs_client.py` → `get_where_used()` anpassen.

### Azure AD

Azure AD als optionale Ergänzung zum API-Key. Beide Methoden werden parallel akzeptiert:

- `X-API-Key: <key>` — für ERP, Scripts, interne Services (kein Azure AD nötig)
- `Authorization: Bearer <Azure AD Token>` — für die SSO-Hauptanwendung (selbe App Registration)

Aktivieren: `AZURE_TENANT_ID` und `AZURE_CLIENT_ID` in `.env` eintragen (gleiche Werte wie in der Haupt-App).

### Deployment

Eigenes `Dockerfile` ist vorhanden. Container bauen und starten:

```bash
cd windchill-api
docker build -t windchill-api .
docker run -p 8001:8001 --env-file .env windchill-api
```

---

## Projektstruktur

```
windchill-api/
├── api.py                      # FastAPI App, Middleware, Router-Einbindung
├── Dockerfile
├── requirements.txt
├── .env.example                # Vorlage für Umgebungsvariablen
└── src/
    ├── core/
    │   ├── config.py           # Einstellungen aus .env (pydantic-settings)
    │   ├── cache.py            # TTL In-Memory-Cache
    │   └── auth.py             # Authentifizierung: API-Key und/oder Azure AD Bearer Token
    ├── adapters/
    │   └── wrs_client.py       # WRS OData HTTP-Client (Auth, CSRF, Retry, Timing)
    ├── models/
    │   └── dto.py              # Pydantic DTOs (entkoppelt von WRS-Schemas)
    ├── services/
    │   └── parts_service.py    # Aggregation, Mapping, Cache-Nutzung
    └── routers/
        └── parts.py            # FastAPI-Endpunkte
```
