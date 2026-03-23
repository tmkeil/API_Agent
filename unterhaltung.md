Was ist ein BOM Export und ist es das gleiche wie ein Export von WTParts aus Windchill?
Copilot said:
Copilot
Kurz gesagt: Ein BOM‑Export ist nicht automatisch das gleiche wie ein Export von WTParts aus Windchill – aber ein WTPart‑Export kann einen BOM‑Export enthalten, je nachdem, wie du ihn erzeugst.

Hier die klare Unterscheidung:

🔧 Was ist ein BOM‑Export?
BOM = Bill of Materials (Stückliste)
Ein BOM‑Export bedeutet, dass die Struktur einer Baugruppe exportiert wird – meist als:

Stücklistenhierarchie (Parent/Child)
Mengenangaben
Positionsnummern
Typen (z. B. Ersatzteil, Kaufteil, Rohteil)
eventuell zusätzliche Metadaten je nach Konfiguration
Typische Formate: CSV, Excel, XML, manchmal auch PLM‑neutrale Formate wie PLMXML.

Ein BOM‑Export beschreibt also die Produktstruktur, nicht unbedingt alle Detailattribute der einzelnen Teile.

🧩 Was ist ein WTPart‑Export in Windchill?
WTParts sind die zentralen Teileobjekte in Windchill.
Ein Export von WTParts kann bedeuten:

Export eines einzelnen WTParts (mit all seinen Attributen)
Export einer gesamten WTPart-Struktur
Export inklusive CAD‑Links, Dokus, Lifecycle‑Infos, etc.
Export als XML, Excel, etc.
Je nach Exportdialog kann das viel mehr enthalten als nur eine BOM.

🆚 Wie unterscheiden sich die beiden?
Thema	BOM‑Export	WTPart‑Export
Fokus	Produktstruktur (Stückliste)	Teilobjekte + Metadaten
Inhalt	Parent/Child‑Beziehungen, Mengen, Rollen	Attribute, Lifecycle, CAD‑Links, Dokus
Format	Häufig CSV/Excel	Oft XML/Excel
Umfang	Relativ schlank	Sehr detailliert (kann aber auch die BOM enthalten)
Fazit:
Ein BOM‑Export ist eine Darstellung der Stückliste,
ein WTPart‑Export ist ein Export der Teile selbst, allerdings kann er die BOM enthalten, wenn du die WTPart‑Struktur auswählst.

Wenn du möchtest …
… kann ich dir gerne erklären:

welche Windchill‑Funktion genau welchen Export erzeugt
wie du einen BOM‑Export vs. WTPart‑Export im UI erkennst
oder wie man beides automatisiert über die Windchill‑REST‑API machen kann
Soll ich weiter ins Detail gehen?









xlsx
neu
You said:
Um diese Daten aus Windchill auszulesen, wie wird das genannt und wo kommt das her? Ist das ein BOM Export? Der Export besteht ja aus den Attributen/Spalten:
Structure Level,
LvL,
Pos,
PTp,
Mat/Doc Number
State
Subtyp
SAP Downstream
Assembly
Parents
Made From
MatScr
MatDest
Plant
DisconType
DisconDate
DisconGrp
SuccessGrp
Description
DocPart
DocType
Version
Quantity
Quantity Unit
PosText
Reference Designator
ERP Position Text
Raw Dimension 1
Raw Dimension 2
Raw Dimension 3
Raw Dimension Unit
Raw Material Amount
Raw Material Amount Unit
Raw Material Quantity
Raw Material Quantity Unit

bekommt man die alle aus Windchill?
Er besteht ja aus verschiedenen Baugruppen und Teilen mit Produkthirarchie, oder?‌
Copilot said:
Copilot
Hier ist die klare, fachlich saubere Antwort auf deine Frage – unter Berücksichtigung der Spalten und Inhalte, die wir im File gesehen haben.
Ich formuliere es so, dass du es intern bei euch sofort einordnen kannst:

✅ Was genau ist das für ein Export?
Der Export, den du zeigst, ist definitiv ein BOM Export aus Windchill – genauer gesagt:

👉 Ein Export der WTPart-Struktur (WTPart Structure Report)
mit zusätzlichen Attributen aus:

der Manufacturing BOM (mBOM)
der Engineering BOM (eBOM)
sowie ERP‑relevanten Attributen (SAP Downstream, Plant, Discon*, Materialdaten etc.)
Er enthält weit mehr als nur die 1:1‑WTPart-Daten oder eine einfache Stückliste.

Dieser Datensatz ist typisch für:

🟦 Windchill: "Structure → Export List to Excel"
oder

🟩 "Export Parts List" / "Export BOM Report"
mit kundenspezifischen zusätzlichen Columns (SAP-Attribute, Raw Material, Discon-Info usw.).

🧩 Warum ist es ein BOM Export?
In deinem Datensatz befinden sich:

✔ Strukturmerkmale
Structure Level
LvL
Parents
Assembly
Quantity / Quantity Unit
→ Das ist immer BOM-Struktur.
✔ WTPart-Daten
Mat/Doc Number
State
Subtyp
DocPart / DocType
Version
✔ Dokumentenlinks
CAD‑Document Drawing
Approval documents (COPYDOWN, COPYFORWARD)
✔ Materialrelevante Attribute
Raw Dimension 1–3
Raw Material Amount
Raw Material Quantity
Material Destination (MatDest)
Material Source (MatScr)
✔ ERP/SAP relevante Felder
SAP Downstream
Plant
PosText / ERP Position Text
DisconType / DisconDate / DisconGrp
SuccessGrp
Diese Kombination gibt es nur, wenn man aus Windchill die WTPart-BOM-Struktur exportiert – oft inkl. kundenspezifischen SAP‑Attributes.

🟢 Ja, man bekommt all diese Daten aus Windchill.
Viele Firmen haben im WTPart ein SAP‑Attributset oder MAPDL‑Set integriert.

🧱 Besteht der Export aus verschiedenen Baugruppen & Teilen?
Ganz klar: Ja.

Das lässt sich eindeutig erkennen:

Produkt (Top-Level):
2200500023 – BES 516‑300‑S299‑S4‑D
neu

darunter:
ASSEMBLY 1 (1200500063)
neu

darunter die Parts:

PART 1 (1200500149)
PART 2 (1200500065)
PART 3 (1200500064)
PART 4 (S1200137291)
neu
und pro Teil:

1..n Zeichnungen
1..n Approval Docs
Materialdaten
SAP‑Attribute usw.
➡️ Das ist eine klassische WTPart‑Stücklistenhierarchie.

💡 Ist das das gleiche wie ein “WTPart Export”?
Kurz: Nein, nicht ganz – aber verwandt.

Ein reiner WTPart-Export (z. B. "Export as XML") würde nur 1 Teil + seine Attribute exportieren.
Was du hast ist:

👉 WTPart-Strukturexport (eine ganze Baumstruktur)
also ein BOM‑Export, nicht ein Einzelteil‑Export.

🔍 Woher kommt alles im Detail?
Spalte	Herkunft in Windchill
Structure Level / LvL / Parents	WTPart Structure Tree
Quantity / Unit	Uses‑Link (WTPart Usage)
Description, Version, DocType	WTPart + WTDocument
SAP Downstream, Plant, Discon*, SuccessGrp	ERP-Kompatibilitätsattribute (Integration Layer)
Raw Material, Dimensions	WTPart‑IBA / MPM‑IBA
CAD‑Document Drawing	EPMDocument-Link (EPM‑WTPart-Association)
Approval document	WTDocument (Lifecycle, Promotion Request etc.)
Pos, PosText, ERP Position Text	Positionsdaten aus Uses-BOM
Subtyp	WTPart Subtype
➡️ Alles ist aus Windchill auslesbar.
➡️ Die Vielzahl der Felder deutet auf kundenspezifische Attributsets + SAP‑Schnittstelle hin.

🧭 Fazit (kurz und klar)
✔ Ja, das ist ein BOM Export aus Windchill.
✔ Er stammt aus dem WTPart-Struktur-Export.
✔ Er bildet mehrere Baugruppen mit kompletter Produkthierarchie ab.
✔ Die vielen Zusatzfelder zeigen eine SAP‑integrierte Umgebung.
✔ Es ist nicht dasselbe wie ein einfacher WTPart‑Export – es ist mehr.

Wenn du willst, kann ich dir:

🔧 erklären, wie man genau diesen Export im UI erzeugt,
🧱 eine grafische Darstellung der Struktur machen,
⚙️ oder ein Mapping aller Felder zu Windchill‑Objekten erstellen.

Soll ich dir z. B. die Strukturhierarchie als Diagramm visualisieren?

Quellen
xlsx







You said:
Ich bin gerade dabei eine API zu bauen, die über die Schnittstelle solche Exports generiert. Meine Frage ist, das sind ja nicht die vollständigen Daten aus dem Windchill System. Hat jemand einen Filter angewendet? Ist dieser Filter oder irgendein anderes Kriterium aus der Excel erkennbar? Was muss ich beachten, wenn ich die API baue? Müssen Input Felder für User existieren? Wenn man den Export auch aus der Windchill API realisieren kann, wieso dann eine API dafür? Was ist der Nutzen bzw. der Vorteil?
Copilot said:
Copilot
Super Frage – und genau die richtige, wenn du eine API baust, die solche Exporte systematisch statt manuell erzeugen soll.
Ich fasse dir die wichtigen technischen Punkte kompakt, aber sehr fundiert zusammen.

✅ 1. Sind das vollständige Daten aus Windchill?
Nein.
Der Export in deiner Excel ist nicht vollständig, sondern zeigt ganz klar:

➜ einen vorkonfigurierten BOM‑Export
mit einer definierten Spaltenauswahl (Attribute bundles)
und vermutlich einem Filter auf Struktur + bestimmte Dokumenttypen.

Das siehst du daran, dass:

nicht alle WTPart-Attribute enthalten sind
nicht alle IBA-Werte (custom attributes) enthalten sind
keine Lifecycle-Historie enthalten ist
keine EPM-Details (CAD Features, Representation, Viewables) enthalten sind
keine Alternate/Owner Links etc. auftauchen
D. h. jemand hat für diesen Export einen festen Column‑Set definiert – oft ein Administrator oder die SAP‑Integrationsabteilung im Rahmen einer “Exportable BOM”-Konfiguration.

✅ 2. Ist anhand der Excel erkennbar, ob ein Filter angewendet wurde?
Ja – indirekt.

🔍 Diese Indizien zeigen, dass ein Filter aktiv war:
A) Die Spalten sind konsistent über alle Zeilen gleich
→ Das spricht für eine vordefinierte Anzeige im Struktur-Tab.

B) Dokumenttypen sind gefiltert (nur DRW / DOK / Approval)
→ In einer rohen Struktur wären mehr Dokumente sichtbar (z. B. Neutralfiles, STEP, IGES, PDFs, WTDocuments aller Art).

C) Nur “Uses”-BOM ist enthalten
→ Keine Occurrences, keine Alternate BOM, keine Manufacturing Views.
Das ist typisch für einen Engineering BOM Filter.

D) Keine CAD-Struktur-Ebene (EPMStructure)
→ D. h. CAD-Baugruppenstrukturen wurden nicht exportiert, sondern nur WTParts.

E) Teilweise SAP‑Attribute vorhanden, aber nicht alle
→ Der Admin hat wahrscheinlich ein bestimmtes “ERP Attribute Set” exportierbar gemacht.

➡️ Fazit:
Ja, der Export wurde mit einem vorgegebenen Column-Set UND einem vordefinierten Structure Filter erzeugt.
Das ist der Standard bei Windchill.

✅ 3. Was bedeutet das für die API, die du baust?
Wenn du die Exporte automatisierst, musst du zwei Dinge trennen:

🔷 (1) Strukturfilter
Welche Teile sollen erscheinen?

Wichtige Filter-Parameter, die du supporten musst:

Top WTPart (Root)
BOM-View: Design, Manufacturing, Service
As-Designed / As-Released / As-Modified
Latest vs. Released
Depth:
Full Structure
First Level
Children until doc-level
Include / Exclude Document Links (CAD, DOK, Approvals)
Include substitutes / alternates
Include phantom parts
🔷 (2) Column-Filter (Attributhülle)
Welche Spalten sollen ausgegeben werden?

Usertypisch:

ERP-Attribute (SAP Downstream, Discon, Plant usw.)
CAD-Link-Status
Lifecycle State
Quantity, Unit
Reference Designator
Raw Material Data
Material Specs
Custom IBAs (firmenspezifische Attribute)
✅ 4. Brauchen User Input-Felder?
Ja, wenn deine API für mehrere Use Cases dienen soll.

Typische Input-Felder wären:

Minimal:
wtpartNumber
structureDepth
view=design|manufacturing|service
filter=latest|released
Optional:
includeDocuments=true|false
attributes=[list of attribute names]
includeSAPFields=true|false
unitSystem=metric|imperial
language=de|en
Erweitert:
erpMappingSet=S4|ECC|None
documentTypes=[DRW,DOK,PDF]
excludePartTypes=[Packaging,Software,...]
➡️ Je mehr Flexibilität du erlaubst, desto weniger muss später am API-Code angepasst werden.

✅ 5. Warum eine eigene API, wenn Windchill selbst eine hat?
Sehr wichtige Frage – viele Manager verstehen das erst spät.

🔥 Vorteil 1: Stabilität
Die Windchill-UI oder “Export to Excel”-Funktion ist nicht stabil automatisierbar.
Sie ist nicht als programmatischer Service gedacht.

🔥 Vorteil 2: Reproduzierbarkeit
Manuell erzeugte Exporte sind:

nicht dokumentiert
nicht versioniert
nicht auditierbar
nicht reproduzierbar
Eine API ist:

100 % wiederholbar
automatisierbar
im Backend abgesichert
standardisiert
🔥 Vorteil 3: Integration
SAP, MES, BI, Data Lakes, Digital Twins – alle brauchen standardisierte BOMs.

Eine API kann:

Exporte schedulen
sie im Data Lake ablegen
sie transformieren
sie validieren
sie automatisiert ins ERP pushen
Windchill selbst macht das nicht.

🔥 Vorteil 4: Performance & Konfiguration
Windchill-REST ist oft:

langsam
schwer parametrierbar
nicht geeignet für riesige BOMs (1000+ Positionen)
Deine API kann:

Cachen
Paging
Result-Sets aufteilen
optimierte Queries fahren
dedizierte Datenbank-Views nutzen
Last vom Windchill UI wegnehmen
🔥 Vorteil 5: Unternehmensstandardisierung
Mit einer eigenen API kannst du:

definieren, wie eine “korrekte BOM” aussieht
unterschiedliche Geschäftsbereiche vereinheitlichen
Audit‑Proof Exporte erzeugen
🧭 6. Zusammenfassung für deine API-Konzeption
✔ Der Export in der Excel ist nicht vollständig.
✔ Es wurde ein vordefinierter Filter + Column-Set angewendet.
✔ Deine API muss filterbar & konfigurierbar sein.
✔ User brauchen Eingabefelder für BOM-Optionen.
✔ Eine eigene API hat klare Vorteile: Stabilität, Integration, Automatisierung.
Wenn du willst, kann ich dir:

ein API‑Design (OpenAPI/Swagger) erstellen
eine empfohlene JSON-Struktur für den BOM-Output generieren
oder dir zeigen, welche Windchill-REST-Endpunkte du intern nutzen solltest
Soll ich dir eine Beispiel-API-Spezifikation zusammenstellen?