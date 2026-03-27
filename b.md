Workitem vom Stakeholder erstellt:

Part 1:

Full Blown BOM JSON Export
PRIO: Simple Export: Ausgehend von einem WT Parts, nur absteigend in der spezifischen BOM
Extended Export: Ausgehend vom Design Part, Export aller Downstream Äquivalenz links. ACHTUNG Verbauung im GATH Part beachten, d.h. hier im Baum der BOM nicht weiter abstiegen, da die lokalen Produkte im Gathering ebenfalls verbaut sind.
- Explosion BOM über alle Level
- Explosion aller EPM und WT Documente
- Explosion Made From Beziehungen
Web Tool
Viewer for BOM Structure (+, - Button), Phase 2: Export aufgeklappter Baumbereich
Lean UI
Performanz beachten, Erwartung Simple Export im Minutenbereich (Caching, Parallele Abfragen, Pageing, Expand ber API Calls)
- full mode (gesamter Baum wird direkt gelesen)
- dynamic mode (Start mit Eben 1, beim Aufklappen wird der nächste Zweig geladen


Ergebnis: JSON

Vorgabe Root Part
- Auswahl ob Design oder Manufacturing View, Default Manufacturing
- Baum über alle WT Parts in der Produkthierarchie (Usage Links)
  - Wichtige Attribute
- Unter jedem WT Part alle Dokumente (CAD, Referenced By, Described By)
  - Wichtige Attribute
- Made From Beziehung als zusätzlicher Ast
  - Made From Parameter

```
root
<ID>
<Name>
<Version>
<Description>
<SAP Name>
...
<CAD Documents>
   <Document 1>
      <ID>
      <Name>
      <Version>
      <ERP Downstream Permitted>
      <SAP Name>
      <SAP Document Type>
      <Attribute 1>
      ...
      <Attribute n>
   ...
   <Document X>

<Described By Documents>
   ...
<Referenced By Documents>

<BOM>
   <Position 1>
      <Line Number>
      <Object Number>
         <ID>
         <Name>
         <Version>
         ...
         <CAD Document>
         ...
         <Described By Documents>
         ...
         <Referenced By Documents>
         ...
         <BOM>

      <Sign>
      <Quantity>
      <Unit>
      <Reference Designator>
      <Consume Group>
      <Follow Up Group>

   <Position 2>
      <Line Number>
      <Object Number>
         <ID>
         <Name>
         <Version>
         <BOM/Made From>
            <ID>
            <Name>
            <Version>
            ...
            <RAWtext 1>
            <RAWtext 2>
            ...
   ...

<Position Y>

```

1. Full Blown BOM Export
- Ausgehend von einem WT Parts
- Explosion BOM über alle Level
- Explosion aller EPM und WT Documente
- Explosion Made From Beziehungen





Detail-Tab eines WT Parts:
**Visualization and Attributes:**
Type:	Product		 			 	
Number:	1200207569		 			 	
Name:	BES M12ME-POC40B-S04G-003		 			 	
Revision:	00		 			CN Approver:	
State:	In Work - Draft - Under Review - Active Released - Published - Adjustment - Retired - Obsolete		 			CN Approver Date:	
Status:	Checked in
Modified By:	Erster Migrationsuser
Last Modified:	2025-11-27 01:00 CET



**Identity:**
Description:	
BES M12ME-POC40B-S04G-003
SAP Prj.Nr. 101358
BES M12ME-POC40B-S04G-003
SAP Prj.Nr. P02416

Product Version:	
Source:	Not Applicable
Associated Product Family:	BES
Assembly Mode:	Separable
Gathering Part:	Yes
Configurable Module:	No

Project Number:	
End Item:	Yes
Default Unit:	each
Equivalence Network:
1200207569, BES M12ME-POC40B-S04G-003, 00.1(Design) - S2200236014, BES M12ME-POC40B-S04G-003, 00.1(Manufacturing)

1200207569, BES M12ME-POC40B-S04G-003, 00.1(Design) - 2200207569, BES M12ME-POC40B-S04G-003, 00.1(Manufacturing)

1200207569, BES M12ME-POC40B-S04G-003, 00.1(Design) - S2200304020, BES M12ME-POC40B-S04G-003, AA.5(Manufacturing)


**Characteristics:**
Tagging Phrase:	
Weight [kg] (modeled):	
Weight [kg] (netto):	
Weight [kg] (brutto):


**Control:**
Is Variant:	No
Variant Derived From Number:	
Not permitted for new development and product variants:	No
Customer Specific:	
GxP - Good practice requirement:	
Rework Pending:	Yes
Requires Special Storage Conditions:	No
Requires Special Operational Conditions:	No


**Specific Conformity Requirements:**
SCR Display:	0000-00-000-0-0
SCR Explosion Protection:	0
SCR Functional Safety:	0
SCR FCM Conformity:	0
SCR Radio and Wireless:	0
SCR CCC Conformity:	0
SCR UL/CSA Conformity:	0
SCR 3A / EHEDG Conformity:	0
SCR ECOLAB Conformity:	0
SCR Certification:	0
SCR CopyExact:	0
SCR Trace:	0
By Approval limited Characteristics:	

**SAP**
SAP Name:	BES M18ZI-PSC80B-S04G
SAP Material Type:	FERT
SAP Rollout Strategy:	111
PVID:	PV17406068
SAP Order Code:	BES060M
SAP Cross-Plant Material State:	AK
SAP Assigned Plants:	CN01
Binding:	CN01
Suffix:	INT

Ich glaube suffix kann INT, GATH  oder n.a. sein.
Das sollte man vielleicht wieder über Raw Fields herausfinden,
damit man sieht, welche Attribute es gibt und wie sie befüllt sind.
Aber darauf Achten, dass es auch andere mögliche Werte geben kann, die in der Vergangenheit vielleicht nicht befüllt waren, aber in Zukunft befüllt werden können.



**System:**
State:	In Work - Draft - Under Review - Active Released - Published - Adjustment - Retired - Obsolete
Life Cycle Template:	BAL Default WTPart LCS
Team Template:	
Context:	P - Design
Location:	/P - Design/Article
Created By:	Erster Migrationsuser
Created By (ERP):	
Modified By:	Erster Migrationsuser
Modified By (ERP):	
Last Modified:	2025-11-27 01:00 CET


**Migration Source:**
Legacy ERP source:	S
Legacy ERP name:	BES M12ME-POC40B-S04G-003
Legacy ERP version:	00
Migration Date:	2025-11-27








Meine Notizen:
made from -> Raw Dim1, RAW Dim2, RAW Dim3, Unit, Amount Unit, qty unit

Suffix: INT, GATH, 

Design Part als Equivalenz Links

ein export mit design und manufacturing

AF - anlauffertigung

2 produkte + gathering part

1 + 2 exportieren und gathering in seiner 

dokumente können mehrfach verknüpft sein
baugruppen können merhfach eingebaut sein
caching
(baum nicht nochmal einfügen sondern cachen)

Tobias Mohr
Anbindung über die API an Windchill
Erzeugen neues Doc verknüpfen das Doc
Probleme mit Performance
Expands optimiert
nur die Attribute abfragen, die man wirklich braucht.
