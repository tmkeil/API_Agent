Hier ist ein fokussierter Review der gezeigten Dateien.

Gesamteindruck: sauber strukturiert, gute Trennung per Mixin, lesbare Docstrings, sinnvoller Retry-/Fallback-Ansatz. Die größten Risiken liegen eher in Sicherheit, Thread-Safety, Fehlersemantik und ein paar OData-/HTTP-Details.

Wichtigste Punkte
1. TLS ist effektiv deaktiviert

In mehreren Stellen ist verify=False bzw. verify_tls=False der Default.

Betroffen:

health_windchill() in api.py
WRSClientBase.__init__() in base.py

Das ist für interne Tests okay, für Produktion aber riskant, weil MITM/gefälschte Zertifikate nicht erkannt werden.

Empfehlung

Default auf True
nur per Config für Dev abschaltbar
Warnung loggen, wenn TLS-Verify deaktiviert ist

Beispiel:

self._http = httpx.Client(
    verify=verify_tls,
    timeout=timeout,
    follow_redirects=True,
    headers={"Accept": "application/json"},
)
if not verify_tls:
    logger.warning("TLS verification is disabled for %s", self.base_url)

Und im Healthcheck:

resp = httpx.get(
    f"{url}/servlet/odata/v6/ProdMgmt",
    verify=settings.WRS_VERIFY_TLS,
    timeout=10,
    follow_redirects=True,
)
2. Singleton-Client ist mit httpx.Client und mutablem Zustand heikel

get_service_client() liefert einen globalen WRSClient zurück. Dieser Client enthält:

Cookie-Session
mutable Headers (CSRF_NONCE)
Caches (_part_cache, _bom_nav_strategy, _usage_link_nav)
einen httpx.Client

Das ist für parallele Requests potenziell problematisch. httpx.Client kann zwar wiederverwendet werden, aber euer Objektzustand ist nicht sauber synchronisiert. Der vorhandene self._lock wird praktisch nicht benutzt.

Risiken

CSRF-Header wird von parallelen Requests überschrieben
Discovery-/Cache-Felder können rennen
Session-Cookies teilen sich alle Requests

Empfehlung

entweder pro Request / pro Operation neuen Client erzeugen
oder den Singleton nur für wirklich read-only, thread-safe Nutzung verwenden
mindestens Mutationen absichern

Wenn ihr den Singleton behalten wollt, dann:

self._lock für Header-/Cache-Mutationen verwenden
_raw_get() Header-Update absichern
Strategie-Discovery absichern

Beispiel:

def _raw_get(self, url: str, params: Any = None, timeout: float | None = None) -> httpx.Response:
    resp = self._http.get(url, params=params, timeout=timeout or self._timeout)
    nonce = resp.headers.get("CSRF_NONCE")
    if nonce:
        with self._lock:
            self._http.headers["CSRF_NONCE"] = nonce
    return resp
3. /health/windchill deaktiviert TLS und macht externe Calls synchron im API-Thread

Der Endpoint ist def, nicht async def, und macht pro System Netzwerk-Calls plus DNS/TCP-Connect. Das blockiert Worker. Für gelegentliche Nutzung okay, aber Healthchecks werden oft häufig aufgerufen.

Verbesserung

async def + httpx.AsyncClient
oder zumindest klar als Diagnoseendpoint kennzeichnen, nicht als Readiness-Probe
kürzere Timeouts oder parallelisierte Checks

Außerdem wäre ein reiner GET /ProdMgmt semantisch robuster, wenn die OData-Version aus Config kommt statt hart v6.

4. health_windchill() ignoriert eure zentrale Config teilweise

Dort wird fest v6 verwendet:

f"{url}/servlet/odata/v6/ProdMgmt"

Während der eigentliche Client settings.WRS_ODATA_VERSION nutzt.

Das kann zu falschen Fehlerbildern führen: App funktioniert, Healthcheck meldet rot.

Besser

f"{url}/servlet/odata/{settings.WRS_ODATA_VERSION}/ProdMgmt"
5. Retry-Logik retried auch bei nicht-transienten 5xx pauschal

_get() retried bei allen >=500. Das ist grundsätzlich okay, aber bei dauerhaft falscher URL / falschem Service / Reverse-Proxy-Fehler bringt es wenig.

Zusätzlich fehlen:

Retry für 429
optional Retry nur für idempotente Fehlerklassen
Logging pro Retry-Versuch

Besser

429 mit Retry-After respektieren
Retry-Versuche loggen
eventuell transport/Timeouts granularer konfigurieren
6. find_part() und find_object() sortieren Version/Iteration lexikografisch

Hier:

items.sort(
    key=lambda p: (p.get("Version", ""), p.get("Iteration", "")),
    reverse=True,
)

Das ist potenziell falsch, wenn Iterationen als Strings kommen:

"10" < "2" lexikografisch

Auch Versionen wie A, B, C sind okay, aber gemischte Formate können brechen.

Besser

LatestIteration eq true stärker priorisieren
numerische Iteration parsen, wenn möglich

Zum Beispiel:

def _sort_key(p: dict):
    version = p.get("Version", "")
    iteration = p.get("Iteration", "")
    try:
        iteration_num = int(iteration)
    except (TypeError, ValueError):
        iteration_num = -1
    latest = p.get("LatestIteration", False)
    return (latest, version, iteration_num)
7. Wildcards in search_entities()/search_parts() sind dokumentiert, aber nicht wirklich implementiert

In search_entities() steht:

Suchbegriff ... mit Wildcard * oder ?

Die Filter machen aber nur:

Number eq
contains(Number, ...)
contains(Name, ...)

* und ? werden also nicht als Wildcards behandelt, sondern literal durchsucht.

Empfehlung

Entweder Doku anpassen
oder Wildcards in OData-Filter übersetzen, z. B.:
ABC* → startswith(Number,'ABC')
*ABC* → contains(Number,'ABC')
8. Potenziell falscher Reverse-Lookup in WhereUsedMixin

Strategie 3:

url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/UsageLinks"
items = self._get_all_pages(url, {"$expand": "Uses"}, return_none_on_error=True)

Das wirkt fraglich für echtes where-used. Von einem Part aus dessen UsageLinks zu lesen liefert oft eher dessen eigene Uses-Struktur statt Parent-Verwendungen. Ob das in eurem WRS-Modell stimmt, ist systemabhängig, aber als generischer Fallback ist es unsicher.

Empfehlung

diese Strategie klar kommentieren als installationsabhängig
Ergebnisse validieren: Parent darf nicht die gleiche ID wie part_id sein
wenn möglich dedizierte Reverse-Navigation oder serverseitige Action bevorzugen
9. search_entities() bricht pro Entity-Typ zu früh ab

Wenn ein Entity-Set oder Service bei einem Filter None liefert:

if items is None:
    break

Dann werden die restlichen Filter für diesen Typ übersprungen. Das ist sinnvoll, wenn der ganze Service fehlt. Aber None kann auch von transientem Fehler kommen, weil _get_all_pages(... return_none_on_error=True) sehr grob ist.

Folge
Ein temporärer Fehler im ersten Filter kann den ganzen Typ unvollständig machen.

Besser

unterscheiden zwischen „Service nicht vorhanden“ und „temporärer Fehler“
z. B. Status/Exception mitgeben statt bloß None
10. _get_all_pages() verschluckt Fehler zu stark

Diese Methode gibt je nach Modus [] oder None zurück und fängt fast alles pauschal ab:

except Exception:
    ...
    return None if return_none_on_error else []

Das macht Aufruferlogik bequem, aber Debugging schwer. Man verliert:

ob Auth-Fehler vorlag
ob Timeout vorlag
ob JSON kaputt war
ob Pagination-Link fehlerhaft war

Besser

mindestens Debug-Logging mit URL, Seite, Fehlerklasse
optional Result-Objekt oder Exception differenzierter weiterreichen
Kleinere Punkte
11. self._lock ist ungenutzt

Er ist deklariert, wird aber praktisch nicht verwendet. Entweder konsequent nutzen oder entfernen.

12. settings wird in base.py importiert, aber nicht verwendet
from src.core.config import settings

Kann raus.

13. Response-Timing-Middleware loggt nur bei Erfolg von call_next()

Wenn call_next() eine Exception wirft, setzt ihr keinen Header und loggt die Zeit nicht.

Robuster

@app.middleware("http")
async def add_timing_headers(request: Request, call_next):
    t0 = time.monotonic()
    try:
        response = await call_next(request)
    finally:
        elapsed_ms = round((time.monotonic() - t0) * 1000, 1)
        if settings.LOG_TIMING:
            logger.info("%s %s (%.1f ms)", request.method, request.url.path, elapsed_ms)
    if 'response' in locals():
        response.headers["X-Response-Time-Ms"] = str(elapsed_ms)
        return response
    raise
14. uvicorn.run("api:app", ...) ist fragil

Datei liegt laut Pfad unter windchill-api/api.py. "api:app" funktioniert nur, wenn das aktuelle Working Directory exakt passt.

Sauberer

entweder Start per CLI dokumentieren
oder Modulpfad eindeutig machen
15. Healthcheck importiert innerhalb der Funktion

Das ist nicht falsch, aber inkonsistent. Wenn Absicht: okay. Sonst lieber oben zentral importieren.

16. Kein explizites Schließen des Singleton-Clients

get_service_client() erstellt einen langlebigen Client, aber ich sehe keinen Shutdown-Hook für close().

Für FastAPI wäre sauber:

@app.on_event("shutdown")
def shutdown_event():
    from src.adapters.wrs_client import _service_client
    if _service_client is not None:
        _service_client.close()
Was ich am Code gut finde
klare Trennung in Mixins
gute Docstrings mit echter Betriebslogik
sinnvolle mehrstufige Fallbacks für Windchill-Unterschiede
return_none_on_error=True als bewusste Semantik ist nützlich
deduplizierte Sammlungen über seen / IDs
saubere kapselnde Basis-Klasse für HTTP/Auth
Meine Priorisierung

Sofort verbessern

TLS-Verify standardmäßig aktivieren
Singleton-/Thread-Safety prüfen
Healthcheck auf Config-Version umstellen
Shutdown-Close für Service-Client ergänzen

Danach
5. Sortierung Version/Iteration robuster machen
6. Wildcard-Doku und Implementierung angleichen
7. Fehlerbehandlung in _get_all_pages() differenzierter machen

Später
8. Async/parallel Healthcheck
9. Retry-Strategie verfeinern
10. Where-used-Fallback fachlich gegen echtes Windchill-Verhalten validieren

Wenn du willst, mache ich dir als Nächstes ein konkretes Patch-Set mit diff-Vorschlägen für die 5 wichtigsten Fixes.















Hier sind die wichtigsten Findings im gezeigten Stand:

expandedOnly-Export verliert Strukturinformation bei nicht aufgeklappten Knoten
In src/routers/admin.py wird in _frontend_tree_to_export() der Wert children_type ausschließlich aus len(children) > 0 berechnet. Bei einem Frontend-Node, der hasChildren=true hat, aber aktuell nicht expandiert wurde, landet er als "no additional children" im Export. Das ist fachlich falsch: der Export behauptet damit, es gebe keine weiteren Kinder, obwohl nur der aktuelle UI-Zustand exportiert wurde.
Betroffene Stelle:

children_type = "subassembly" if has_children else "no additional children"

Folge: Der JSON-Export ist irreführend und kann downstream als vollständige Aussage über die BOM interpretiert werden, obwohl er nur die expandierten UI-Knoten enthält.

hasChildren ist im BOM-Tree praktisch immer true
In src/services/parts_service.py setzt _map_tree_node():

hasChildren=bool(n["id"])

Sobald ein Part eine ID hat, wird hasChildren=True gesetzt — unabhängig davon, ob tatsächlich Unterbaugruppen/Kinder existieren. Für Blattknoten ist das falsch.

Folge: Das Frontend zeigt expandierbare Knoten an, obwohl am Ende keine Kinder existieren. Das erzeugt unnötige Requests und inkonsistentes UX-Verhalten.

Generische Suche liefert fachlich falsches DTO-Feld für Nicht-Parts
search_service.search_parts() ist inzwischen eine Multi-Entity-Suche, gibt aber weiterhin PartSearchResult zurück. Darin heißt die ID-Spalte partId, obwohl auch WTDocument, EPMDocument, WTChangeOrder2 usw. zurückgegeben werden.
Betroffene Stellen:

src/models/dto.py → class PartSearchResult
src/services/search_service.py → Multi-Entity-Mapping auf PartSearchResult
windchill-frontend/src/api/client.ts → searchParts()

Folge: API-Vertrag und Semantik passen nicht mehr zusammen. Das funktioniert technisch noch, ist aber ein klares Design-Leck und wird später leicht zu Bugs führen, sobald Frontend/Backend annehmen, dass partId wirklich nur für Parts gilt.

Cache für Part-Detail ist nicht mandanten-/systemabhängig
In get_part_detail() wird global gecacht mit:

cache_key = f"detail:{code}"

Der Key berücksichtigt weder Windchill-System noch Benutzer/Session. Bei mehreren Systemen oder abweichenden Berechtigungen kann derselbe Code auf unterschiedliche Objekte oder unterschiedliche Sichtbarkeit zeigen.

Folge: Falsche Daten können zwischen Systemen oder Sessions wiederverwendet werden.

Where-Used quantity/unit sind nicht robust normalisiert
In get_part_where_used() wird quantity=p.get("Quantity") direkt übernommen, während an anderen Stellen Quantity-Dicts mit Value/Unit normalisiert werden. Wenn WRS hier ebenfalls strukturierte Quantity-Objekte liefert, landet im DTO unter quantity: Optional[float] ein Dict.

Folge: Response-Validierung oder Frontend-Verarbeitung kann brechen, abhängig vom tatsächlichen WRS-Payload.

Insgesamt ist das Refactoring sinnvoll, vor allem dependencies.py und odata.py. Die zwei Punkte, die ich am ehesten sofort fixen würde, sind hasChildren und der Export von nicht expandierten BOM-Knoten.













Ich sehe den Frontend-Stand. Das ist insgesamt schon sauber strukturiert: Routing, geschützte Bereiche, Detail-Tabs und wiederverwendbare BOM-Komponente passen gut zusammen.

Die wichtigsten Punkte, die ich direkt sehe:

1. StructureTab ruft load() während des Renderns auf
Das ist der kritischste Punkt. Hier:

if (!loaded && !loading && !error) {
  load()
}

Ein Async-Call im Render ist in React problematisch und kann zu mehrfachen Requests oder unerwartetem Verhalten führen. Das sollte in ein useEffect.

Sauberer:

useEffect(() => {
  if (!loaded) {
    load()
  }
}, [loaded, load])

2. BomTreeNodeComponent: leere CAD-Dokumente werden bei "Keine Unterelemente" nicht berücksichtigt
Hier:

{loaded && children.length === 0 && documents.length === 0 && (
  <div ...>Keine Unterelemente</div>
)}

Wenn cadDocuments vorhanden sind, könnte trotzdem fälschlich „Keine Unterelemente“ erscheinen. Besser:

{loaded && children.length === 0 && documents.length === 0 && cadDocuments.length === 0 && (
  <div ...>Keine Unterelemente</div>
)}

3. DashboardPage: TYPE_KEY_MAP wird vor Deklaration benutzt
In handleSearch und handleRowClick greifst du auf TYPE_KEY_MAP zu, obwohl es weiter unten als const definiert ist. Das funktioniert zur Laufzeit nur, wenn der Callback erst später ausgeführt wird, ist aber unsauber und potenziell fehleranfällig. Die Mappings besser oberhalb der Callbacks definieren oder komplett außerhalb der Komponente.

4. Uneinheitliche ID-Felder
In PartSearchResult heißt die ID partId, obwohl dort auch Dokumente, CAD-Dokumente und Change-Objekte auftauchen können. Fachlich wäre etwas wie objectId konsistenter.

Ähnlich bei:

DocumentNode.docId
WhereUsedEntry.oid
ObjectDetail.objectId

Das ist nicht kaputt, aber inkonsistent.

5. WhereUsedTab navigiert hart auf /detail/part/...
Hier:

onClick={() => navigate(`/detail/part/${encodeURIComponent(e.number)}`)}

Das ist vermutlich korrekt, wenn Where-Used immer Eltern-Parts liefert. Falls das Backend irgendwann andere Objekttypen zurückgibt, wäre das zu starr. Für jetzt wohl okay, aber fachlich fest verdrahtet.

6. Fehlerbehandlung mit any
Mehrfach:

} catch (e: any) {
  setError(e.message)
}

Besser sicher typisieren:

} catch (e: unknown) {
  setError(e instanceof Error ? e.message : 'Unbekannter Fehler')
}

7. BomTreeNodeComponent: Klick auf gesamte Zeile toggelt immer
Aktuell toggelt jeder Klick auf die ganze Zeile. Das ist UX-seitig okay, kann aber später stören, falls du Links, Context-Menüs oder Detailaktionen in der Zeile brauchst. Dann besser nur den Pfeil oder die Nummer klickbar machen.

8. Sprachmix in UI
Die App ist überwiegend deutsch, aber einige Labels sind gemischt:

Where-Used
Part
Change Notice
Problem Report

Wenn das UI für Endanwender gedacht ist, wäre eine vollständige sprachliche Vereinheitlichung sinnvoll.

9. Doppelte Typ-Labels / Mapping-Definitionen
TYPE_LABELS sind mehrfach verteilt:

DetailHeader
DetailsTab
DashboardPage

Das sollte zentralisiert werden, z. B. in src/constants/objectTypes.ts.

10. LoginPage: autoComplete="new-password" für Login-Passwort
Für ein Login-Formular wäre eher korrekt:

autoComplete="current-password"Ja. Aber

und für Benutzername meist:

autoComplete="username"

Das verbessert Browser-Autofill.

Mein Fazit:
Der Aufbau ist gut und schon ziemlich produktionsnah. Die zwei Punkte, die ich zuerst ändern würde, sind:

StructureTab von Render-Call auf useEffect umbauen
BomTreeNodeComponent-Leerzustand um cadDocuments.length ergänzen

Danach würde ich die Mappings/Labels zentralisieren und das Error-Handling säubern.

Ich kann dir daraus direkt einen konkreten Patch für die betroffenen Dateien machen.