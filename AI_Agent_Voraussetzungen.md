# AI Agent für API und Prozessautomatisierung

---


ein eigener AI Agent in deiner Anwendung ist für deinen Lebenslauf deutlich wertvoller. "Habe einen AI Agent gebaut, der über eine selbst entwickelte API Windchill-BOMs erstellt" schlägt "Habe ein Backend exponiert, damit die firmeninterne Copilot-Plattform es nutzt" um Längen.

Und pragmatisch betrachtet: Wenn du das Backend exponierst, hast du keine Kontrolle mehr darüber, wie gut oder schlecht Copilot damit arbeitet. Wenn der Agent in deiner Anwendung läuft, kannst du Prompts, Workflows und Fehlerhandling selbst steuern.




## Kontext

Das Unternehmen möchte einen AI Agent entwickeln, der Mitarbeiter bei internen Prozessen unterstützt. Der Agent soll auf SAP, ERP und PDM zugreifen, Daten lesen und eintragen, Prozessschritte intelligent überspringen und den Mitarbeiter per Ampelsystem über den Bearbeitungsstand informieren.

Bevor Entwicklung beginnt, müssen folgende Punkte intern geklärt sein.

---

## 1. Datenschutz

Ein AI Agent benötigt ein Sprachmodell (LLM). Jede Anfrage enthält interne Informationen => Compliance Entscheidung.

| Option | Datenhaltung |
|---|---|
| Cloud LLM (Anthropic, OpenAI) | Extern – Daten verlassen das Unternehmen |
| Azure OpenAI / AWS Bedrock | EU-Server, Enterprise-Vertrag möglich |
| On-Premise LLM (Llama, Mistral) | Intern – keine Daten nach außen |

---

## 2. API-Zugang zu den Systemen

PDM-System ist PTC Windchill. ERP-System noch zu klären.

- Welches ERP-System wird eingesetzt?
- Wer vergibt API-Zugänge und was ist der Prozess dafür?
- SAP liefert aktuell 2 Exporte – reicht das, oder wird eine Live-API benötigt?

---

## 3. Berechtigungen & Rollen

Der Agent handelt im Namen des eingeloggten Mitarbeiters und darf nur das tun, was dieser auch manuell dürfte.

- Gibt es ein bestehendes Berechtigungssystem, das der Agent respektieren muss?
- Müssen Aktionen des Agenten protokolliert werden (Audit-Trail)?
- Welche Aktionen brauchen eine menschliche Bestätigung, bevor der Agent sie ausführt?

---

## 4. Scope & Prozesse

Der Agent muss Prozesslogik kennen, um Schritte intelligent überspringen zu können.

- Welche Prozesse sollen zuerst abgedeckt werden?
- Wer dokumentiert die Prozesslogik (Schritte, Abhängigkeiten, Pflichtfelder)?
- Wer definiert die Ampel-Logik: Was ist grün, gelb, rot?

---

## 5. Architektur

Der Agent ist ein autonomes System, das Entscheidungen trifft, Systeme bedient und dabei einen Menschen durch einen Prozess führt. Dafür braucht es vier Schichten:

```
Mitarbeiter (Chat-UI + Ampel)
     1. Agent Backend (Orchestrierung)
      - System-Prompt (Prozessregeln, Ampel-Logik)
      - Tool-Definitionen (Backend-Funktionen, die API-Calls ausführen)
      - RAG-Zugriff (Wissensdatenbank)

     2. Systemschicht
      - PTC Windchill API  (PDM)
      - SAP API / Export   (ERP)
      - ERP API            (Beschaffung, Produktion, Verkauf)
```

---

## 6. System-Prompt vs. RAG vs. API

Dieses Wissen kommt aus drei verschiedenen Quellen, je nach Art der Information.

**System-Prompt**\
Stabile, kurze Prozesslogik wird direkt in den Prompt des Agenten geschrieben (.md Datei).
Das ist das "Betriebshandbuch" für den Agenten.\

**Beispiele:**\
Pflichtfelder, Reihenfolge von Schritten, Ampel-Kriterien.

**RAG**\
Umfangreiche Handbücher, Windchill-Konfigurationsdokus.
Gespeichert als Vektoren in einer Datenbank (ChromaDB oder pgvector), damit der Agent bei Bedarf relevante Informationen abrufen kann.

**Beispiele:**\
Wie fülle ich das Feld X in Windchill aus\
Was passiert, wenn ich Schritt Y überspringe

**Live API-Call**\
Was gerade in Windchill, SAP oder ERP steht, holt der Agent per API-Call.

**Beispiele:**\
Status einer Bestellung\
Lagerbestand

---

## 7. Tool-Definitionen & Backend

Der Agent ruft autonom Funktionen auf, die als "Tools" definiert sind.
Diese Tools sind die einzigen Aktionen, die der Agent ausführen kann.
Das Backend prüft die Berechtigungen, übersetzt die Tool-Aufrufe in echte API-Calls und gibt die Ergebnisse zurück.

**Tools, die entwickelt werden müssen:**

```
windchill_get_document_status(part_number)
windchill_release_drawing(part_number, user_id)
sap_get_order(order_id)
sap_create_purchase_order(data)
erp_check_stock(material_id)
erp_update_production_status(order_id, status)
check_process_completeness(step, context) → gibt Ampelstatus zurück
```

---

## 8. Was ich brauche

- Zugriff auf Test-Accounts in Windchill, SAP und ERP für die Entwicklung und das Testing der Tools
- Prozessdokumentation aller relevanten Abläufe
- Ampel-Kriterien: Wann ist ein Schritt grün, gelb, rot?
- Welche Aktionen darf der Agent autonom ausführen, und welche brauchen eine menschliche Bestätigung?
- Bestehende Handbücher und SOPs als Grundlage für die RAG-Datenbank

---

## 9. Technologie-Stack (Empfehlung)

| Schicht | Technologie | Begründung |
|---|---|---|
| LLM | Je nach Datenschutz-Entscheidung (siehe Punkt 1) | — |
| Agent-Orchestrierung | MCP (Model Context Protocol) | Anthropics Standard für Tool-Use-Agenten |
| Backend | Python (FastAPI) oder Node.js | Schlanke REST-API als Mittler zu den Systemen |
| RAG-Datenbank | ChromaDB (einfach) oder pgvector (skalierbar) | Vektorsuche über Prozessdokumente |
| Frontend | React + Tailwind | Chat-UI mit Ampel-Komponente |
| Auth | OAuth2 / Active Directory | Berechtigungen vom Mitarbeiter-Account erben |
| Windchill-Anbindung | PTC Windchill REST API (ab Version 12) | Offizielle Schnittstelle für Dokumente & Status |