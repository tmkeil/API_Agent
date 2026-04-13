
Option Explicit

' ===== VBA7 / VBA6 KOMPATIBILITÄT =====
' VBA7: Office 2010+ (64-bit und 32-bit)
' VBA6: Office 2007 und älter (nur 32-bit)
' Sleep-Funktion aus Windows kernel32.dll für CPU-freundliches Warten
' Unterschied: VBA7 benötigt PtrSafe und LongPtr für 64-bit Kompatibilität
#If VBA7 Then
    Private Declare PtrSafe Sub Sleep Lib "kernel32" (ByVal ms As LongPtr)  ' Office 2010+ (64-bit/32-bit)
#Else
    Private Declare Sub Sleep Lib "kernel32" (ByVal ms As Long)              ' Office 2007 und älter (32-bit)
#End If

' ===== GLOBALE GUARDS: Verhindert Race Conditions und Reentrancy =====
' gBusy: Verhindert dass mehrere Buttons gleichzeitig ausgeführt werden
'        Beispiel: User klickt schnell Button A und B hintereinander
'        -> Nur einer wird ausgeführt, der andere wird ignoriert
Private gBusy As Long

' gPickerActive: Verhindert doppelte FileDialog-Aufrufe
'                Beispiel: User klickt mehrfach auf Import-Button während Dialog offen
'                -> Nur ein Dialog wird geöffnet
Private gPickerActive As Boolean

' gButtonSheet: Speichert das Sheet auf dem die Workflow-Buttons sind
'               Wird beim ersten Zugriff automatisch ermittelt
Private gButtonSheet As Worksheet
Private gConfigSheet As Worksheet

' Async Import: Module-Level State für Application.OnTime Callback
Private mImportRows As Long
Private mImportStart As Double

' ===== BUTTON-NAMEN KONSTANTEN =====
' WICHTIG: Diese Namen müssen mit den tatsächlichen Button-Namen in Excel übereinstimmen!
' 
' So finden Sie die Button-Namen in Excel:
'   1. Klicken Sie auf einen Button
'   2. Schauen Sie in die Namensbox (links neben der Formelleiste)
'   3. Dort steht der Name, z.B. "Button 1", "Button 2", etc.
' 
' Oder in VBA (Alt+F11 -> Strg+G für Immediate Window):
'   For Each btn In ActiveSheet.Buttons: Debug.Print btn.Name: Next
' 
Private Const BTN_IMPORT As String = "Button 1"  ' Import-Button - ANPASSEN!
Private Const BTN_A As String = "Button 3"        ' Button für PartA - ANPASSEN!
Private Const BTN_B As String = "Button 4"        ' Button für PartB - ANPASSEN!
Private Const BTN_C As String = "Button 5"        ' Button für PartC - ANPASSEN!
Private Const BTN_D As String = "Button 6"        ' Button für Export - ANPASSEN!

'==================== Config Sheet Management ====================
' Initialisiert das Config-Sheet (erstellt es falls nicht vorhanden)
' Setzt es auf xlSheetVeryHidden damit normale User es nicht sehen
' WICHTIG: Wenn User es sichtbar gemacht hat, wird es NICHT automatisch versteckt!
Private Sub InitializeConfigSheet()
    Dim ws As Worksheet
    Dim headerRow As Range
    Dim wasVisible As XlSheetVisibility
    
    ' Prüfe ob Config-Sheet bereits existiert und merke Sichtbarkeit
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("_Config")
    If Not ws Is Nothing Then
        wasVisible = ws.Visible  ' Aktuelle Sichtbarkeit merken
    End If
    On Error GoTo 0
    
    ' Wenn nicht vorhanden, erstelle es
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets.Add(Before:=ThisWorkbook.Worksheets(1))
        ws.Name = "_Config"
        wasVisible = xlSheetVeryHidden  ' Neu erstelltes Sheet soll versteckt sein
        
        ' Header-Zeile erstellen
        ws.Range("A1").Value = "Setting Name"
        ws.Range("B1").Value = "Value"
        ws.Range("C1").Value = "Description"
        
        ' Header formatieren
        Set headerRow = ws.Range("A1:C1")
        headerRow.Font.Bold = True
        headerRow.Interior.Color = RGB(200, 200, 200)
        
        ' Standard-Konfigurationen erstellen
        ws.Range("A2").Value = "ApplyPrintingGoodRule"
        ws.Range("B2").Value = "YES"
        ws.Range("C2").Value = "Remove Enclosed Documentation with Printing Good=No/False (YES/NO)"
        
        ws.Range("A3").Value = "FilterQepDrwDocTypes"
        ws.Range("B3").Value = "NO"
        ws.Range("C3").Value = "Remove rows with DocType QEP or DRW"
        
        ws.Range("A4").Value = "ExportPath"
        ws.Range("B4").Value = "C:\TEMP"
        ws.Range("C4").Value = "Default directory for CSV export"
        
        ' Spaltenbreiten anpassen
        ws.Columns("A:A").ColumnWidth = 30
        ws.Columns("B:B").ColumnWidth = 15
        ws.Columns("C:C").ColumnWidth = 50
    End If
    
    ' Sheet nur verstecken wenn es NICHT vom User sichtbar gemacht wurde
    ' Wenn User ShowConfigSheet() aufgerufen hat: wasVisible = xlSheetVisible
    ' In diesem Fall NICHT automatisch verstecken!
    If wasVisible = xlSheetVeryHidden Then
        ws.Visible = xlSheetVeryHidden
    End If
    
    ' Cache für zukünftige Zugriffe
    Set gConfigSheet = ws
End Sub

' Liest einen Config-Wert aus dem Config-Sheet
' Return: Wert als String, oder "" wenn nicht gefunden
Private Function GetConfigValue(ByVal settingName As String) As String
    If gConfigSheet Is Nothing Then InitializeConfigSheet
    
    Dim ws As Worksheet: Set ws = gConfigSheet
    Dim lastRow As Long, i As Long
    
    ' Finde letzte Zeile mit Daten
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    ' Suche Setting (ab Zeile 2, da Zeile 1 = Header)
    For i = 2 To lastRow
        If Trim(CStr(ws.Cells(i, 1).Value)) = settingName Then
            GetConfigValue = Trim(CStr(ws.Cells(i, 2).Value))
            Exit Function
        End If
    Next i
    
    ' Nicht gefunden
    GetConfigValue = ""
End Function

' Schreibt einen Config-Wert in das Config-Sheet
' Erstellt neuen Eintrag wenn Setting noch nicht existiert
Private Sub SetConfigValue(ByVal settingName As String, ByVal value As String)
    If gConfigSheet Is Nothing Then InitializeConfigSheet
    
    Dim ws As Worksheet: Set ws = gConfigSheet
    Dim lastRow As Long, i As Long, found As Boolean
    
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    ' Suche existierendes Setting
    For i = 2 To lastRow
        If Trim(CStr(ws.Cells(i, 1).Value)) = settingName Then
            ws.Cells(i, 2).Value = value
            found = True
            Exit For
        End If
    Next i
    
    ' Wenn nicht gefunden, neue Zeile hinzufügen
    If Not found Then
        ws.Cells(lastRow + 1, 1).Value = settingName
        ws.Cells(lastRow + 1, 2).Value = value
    End If
End Sub

' Prüft ob eine Regel aktiviert ist (YES/NO)
' Return: True wenn "YES", False bei "NO" oder nicht vorhanden
Private Function IsRuleEnabled(ByVal ruleName As String) As Boolean
    Dim value As String
    value = UCase(Trim(GetConfigValue(ruleName)))
    IsRuleEnabled = (value = "YES")
End Function

'==================== Config Sheet - Admin Functions ====================
' NUR FÜR POWER-USER: Macht Config-Sheet sichtbar zum Editieren
Public Sub ShowConfigSheet()
    InitializeConfigSheet
    If Not gConfigSheet Is Nothing Then
        gConfigSheet.Visible = xlSheetVisible
        gConfigSheet.Activate
        MsgBox "Config sheet is now visible. Remember to hide it again after editing!", vbInformation, "Config Sheet"
    End If
End Sub

' NUR FÜR POWER-USER: Versteckt Config-Sheet wieder
Public Sub HideConfigSheet()
    InitializeConfigSheet
    If Not gConfigSheet Is Nothing Then
        gConfigSheet.Visible = xlSheetVeryHidden
        MsgBox "Config sheet is now hidden.", vbInformation, "Config Sheet"
    End If
End Sub

' EINMALIG AUSFÜHREN: Fügt fehlende Config-Einträge hinzu
Public Sub UpdateConfigSheet()
    InitializeConfigSheet
    If gConfigSheet Is Nothing Then Exit Sub
    
    Dim ws As Worksheet: Set ws = gConfigSheet
    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    
    ' Liste aller erwarteten Config-Einträge: Name, Standardwert, Beschreibung
    Dim cfgNames As Variant, cfgDefaults As Variant, cfgDescs As Variant
    cfgNames = Array("ApplyPrintingGoodRule", "FilterQepDrwDocTypes", "ExportPath")
    cfgDefaults = Array("YES", "NO", "C:\TEMP")
    cfgDescs = Array( _
        "Remove Enclosed Documentation with Printing Good=No/False (YES/NO)", _
        "Remove rows with DocType QEP or DRW (YES/NO)", _
        "Default directory for CSV export")
    
    Dim k As Long, found As Boolean, addedCount As Long
    addedCount = 0
    
    For k = LBound(cfgNames) To UBound(cfgNames)
        found = False
        Dim i As Long
        For i = 2 To lastRow
            If UCase(Trim(CStr(ws.Cells(i, 1).Value))) = UCase(CStr(cfgNames(k))) Then
                found = True
                ' Beschreibung aktualisieren (falls geändert)
                ws.Cells(i, 3).Value = CStr(cfgDescs(k))
                Exit For
            End If
        Next i
        
        If Not found Then
            lastRow = lastRow + 1
            ws.Cells(lastRow, 1).Value = CStr(cfgNames(k))
            ws.Cells(lastRow, 2).Value = CStr(cfgDefaults(k))
            ws.Cells(lastRow, 3).Value = CStr(cfgDescs(k))
            addedCount = addedCount + 1
        End If
    Next k
    
    If addedCount > 0 Then
        MsgBox addedCount & " config option(s) added!", vbInformation, "Config Updated"
    Else
        MsgBox "All config options already exist. Descriptions updated.", vbInformation, "Config OK"
    End If
End Sub

' Findet und speichert das Sheet auf dem die Workflow-Buttons sind
' Sucht nach "Button 1" (Import-Button) auf allen Sheets
' Return: Worksheet-Objekt mit den Buttons, oder Nothing falls nicht gefunden
Private Function GetButtonSheet() As Worksheet
    ' Bereits gefunden? Dann cached Version zurückgeben
    If Not gButtonSheet Is Nothing Then
        Set GetButtonSheet = gButtonSheet
        Exit Function
    End If
    
    ' Suche Button 1 auf allen SICHTBAREN Sheets (xlSheetVeryHidden überspringen!)
    Dim ws As Worksheet
    Dim testShape As Shape
    
    For Each ws In ThisWorkbook.Worksheets
        ' Überspringe sehr versteckte Sheets (z.B. _Config)
        If ws.Visible <> xlSheetVeryHidden Then
            ' Versuche "Button 1" zu finden - SHAPES, nicht Buttons!
            On Error Resume Next
            Set testShape = Nothing
            Set testShape = ws.Shapes("Button 1")
            On Error GoTo 0
            
            If Not testShape Is Nothing Then
                Set gButtonSheet = ws  ' Gefunden! Speichern für zukünftige Aufrufe
                Set GetButtonSheet = ws
                Exit Function
            End If
        End If
    Next ws
    
    ' Fallback: Erstes Sheet verwenden
    Set gButtonSheet = ThisWorkbook.Worksheets(1)
    Set GetButtonSheet = gButtonSheet
End Function

' ===== TEST: Zeigt alle Button-Namen an =====
' Führen Sie diese Funktion einmal aus (Alt+F8 -> Test_ShowButtonNames)
' Kopieren Sie dann die richtigen Namen in die Konstanten oben
Public Sub Test_ShowButtonNames()
    Dim shp As Object
    Dim msg As String
    
    msg = "ALL SHAPES on this sheet (including buttons):" & vbCrLf & vbCrLf
    
    On Error Resume Next
    ' Zeige ALLE Shapes (nicht nur Buttons-Collection)
    For Each shp In ActiveSheet.Shapes
        msg = msg & "Name: " & shp.Name
        msg = msg & " | Type: " & shp.Type
        If shp.Type = 8 Then msg = msg & " (Button/Form Control)"
        msg = msg & vbCrLf
    Next shp
    On Error GoTo 0
    
    MsgBox msg, vbInformation, "All Shape Names"
End Sub

' ===== BUTTON-STEUERUNG: Aktiviert/Deaktiviert Buttons basierend auf Workflow-Status =====
' Versteckt Buttons während Verarbeitung
Private Sub DisableAllButtons()
    Dim ws As Worksheet: Set ws = GetButtonSheet()
    If ws Is Nothing Then Exit Sub
    
    On Error GoTo ButtonNameError
    ws.Shapes("Button 1").Visible = False
    ws.Shapes("Button 3").Visible = False
    ws.Shapes("Button 4").Visible = False
    ws.Shapes("Button 5").Visible = False
    ws.Shapes("Button 6").Visible = False
    On Error GoTo 0
    
    DoEvents
    Exit Sub
    
ButtonNameError:
    MsgBox "ERROR: Button names do not match!" & vbCrLf & vbCrLf & _
           "Please run 'Test_ShowButtonNames' (Alt+F8) to see the actual button names." & vbCrLf & vbCrLf & _
           "Then update the button names in DisableAllButtons() and EnableAllButtons().", _
           vbCritical, "Button Name Mismatch"
End Sub

' Aktiviert Buttons progressiv basierend auf erfolgreichem Workflow-Schritt
' Import-Button wird immer aktiviert (außer bei step=0)
' step = 0: Alle deaktiviert (Initial-Zustand)
' step = 1: Import + Button A aktiviert (nach Import)
' step = 2: Import + Button A+B aktiviert (nach PartA)
' step = 3: Import + Button A+B+C aktiviert (nach PartB)
' step = 4: Import + Button A+B+C+D aktiviert (nach PartC)
Private Sub EnableButtonsUpTo(ByVal step As Integer)
    Dim ws As Worksheet: Set ws = GetButtonSheet()
    If ws Is Nothing Then Exit Sub
    
    On Error Resume Next
    ' Zuerst alle unsichtbar machen
    DisableAllButtons
    
    ' Import-Button immer sichtbar machen (außer bei step=0)
    If step > 0 Then ws.Shapes("Button 1").Visible = True
    
    ' Dann schrittweise Workflow-Buttons sichtbar machen
    If step >= 1 Then ws.Shapes("Button 3").Visible = True
    If step >= 2 Then ws.Shapes("Button 4").Visible = True
    If step >= 3 Then ws.Shapes("Button 5").Visible = True
    If step >= 4 Then ws.Shapes("Button 6").Visible = True
    On Error GoTo 0
    
    ' WICHTIG: Screen Update erzwingen damit Änderungen sichtbar werden
    Application.ScreenUpdating = True
    DoEvents
    Application.ScreenUpdating = False
End Sub

' Aktiviert ALLE Buttons SOFORT (keine Wartezeit)
Private Sub EnableAllButtons()
    Dim ws As Worksheet: Set ws = GetButtonSheet()
    If ws Is Nothing Then Exit Sub
    
    On Error GoTo ButtonNameError
    ws.Shapes("Button 1").Visible = True
    ws.Shapes("Button 3").Visible = True
    ws.Shapes("Button 4").Visible = True
    ws.Shapes("Button 5").Visible = True
    ws.Shapes("Button 6").Visible = True
    On Error GoTo 0
    
    DoEvents
    Exit Sub
    
ButtonNameError:
    MsgBox "ERROR: Button names do not match!" & vbCrLf & vbCrLf & _
           "Please run 'Test_ShowButtonNames' (Alt+F8) to see the actual button names." & vbCrLf & vbCrLf & _
           "Then update the button names in DisableAllButtons() and EnableAllButtons().", _
           vbCritical, "Button Name Mismatch"
End Sub

' Aktiviert Buttons VERZÖGERT per Application.OnTime.
' VBA beendet sich komplett → Excel kann noch laufende Berechnungen
' (z.B. PartB/C nach SetNamedRange "ToDoRegion") fertig verarbeiten,
' BEVOR der User den nächsten Button klicken kann.
Public Sub EnableAllButtonsDelayed()
    Application.OnTime Now + TimeSerial(0, 0, 3), "EnableAllButtons_Callback"
End Sub

Public Sub EnableAllButtons_Callback()
    EnableAllButtons
    ExitBusy
End Sub

' ===== EINMALIGE CLEANUP FUNKTION =====
' NUR EINMAL AUSFÜHREN: Löscht ALLE Named Ranges (auch alte External:=True Ranges)
' Danach NIE MEHR AUFRUFEN! PartA/B/C müssen danach neu erstellt werden
Public Sub ONCE_DeleteAllNamedRanges()
    Dim nm As Name
    Dim countDeleted As Long: countDeleted = 0
    
    On Error Resume Next
    For Each nm In ThisWorkbook.Names
        nm.Delete
        countDeleted = countDeleted + 1
    Next nm
    On Error GoTo 0
    
    MsgBox "Deleted " & countDeleted & " Named Ranges." & vbCrLf & vbCrLf & _
           "NEXT STEPS:" & vbCrLf & _
           "1. Save workbook (Ctrl+S)" & vbCrLf & _
           "2. Close and reopen workbook" & vbCrLf & _
           "3. Run Import to create SourceRegion" & vbCrLf & _
           "4. Create PartA/B/C Python cells and name them" & vbCrLf & _
           "5. From now on they will stay!", vbInformation, "Cleanup Complete"
End Sub

' ===== NOTFALL: Alle Buttons wieder einblenden =====
' Für den Fall dass Buttons nach einem Absturz/Timeout versteckt blieben.
' Ausführen: Alt+F8 -> RESCUE_ShowButtons -> Ausführen
' Oder: Alt+F11 -> Strg+G -> RESCUE_ShowButtons -> Enter
Public Sub RESCUE_ShowButtons()
    ' Globale Guards zurücksetzen
    gBusy = 0
    Application.Cursor = xlDefault
    Application.Interactive = True
    Application.EnableEvents = True
    SafeStatusBar False
    
    ' Alle Buttons auf ALLEN sichtbaren Sheets einblenden
    Dim ws As Worksheet, shp As Shape
    For Each ws In ThisWorkbook.Worksheets
        If ws.Visible <> xlSheetVeryHidden Then
            On Error Resume Next
            For Each shp In ws.Shapes
                shp.Visible = True
            Next shp
            On Error GoTo 0
        End If
    Next ws
    
    MsgBox "All buttons restored. Application state reset.", vbInformation, "Rescue Complete"
End Sub

' ===== LÖSCHT DATEN IN DEN DREI ARBEITS-SHEETS =====
' Sheets: "source" (Import), "ToDo (User)" (Transformation), "destination" (Export)
' WICHTIG: Löscht auch Named Ranges um inkonsistente Zustände zu vermeiden
' KRITISCH: Löscht NUR Daten-Ranges, NICHT Python-Formeln (PartA, PartB, PartC)!
Public Sub Clear_DataSheets()
    Dim ws As Worksheet
    Dim names As Variant
    ' Array mit den drei Sheet-Namen die geleert werden sollen
    names = Array("source", "ToDo (User)", "destination")

    On Error Resume Next  ' Fehler ignorieren falls Sheet nicht existiert
    For Each ws In ThisWorkbook.Worksheets
        ' Application.Match: Prüft ob Sheet-Name im Array enthalten ist
        ' Gibt Index zurück wenn gefunden, sonst #N/A Fehler
        ' IsError(...) = False bedeutet: Sheet-Name wurde im Array gefunden
        If Not IsError(Application.Match(ws.Name, names, 0)) Then
            ws.Cells.ClearContents    ' Nur Zellinhalte löschen, Format bleibt erhalten
        End If
    Next ws
    On Error GoTo 0  ' Fehlerbehandlung zurücksetzen
    
    ' KRITISCH: Lösche NUR die Daten-Named Ranges, NICHT die Python-Formeln!
    ' Grund: Alte Named Ranges könnten mit External:=True erstellt worden sein
    ' Diese verursachen "externe Verknüpfung" Warnung beim Öffnen
    ' WICHTIG: PartA, PartB, PartC NICHT löschen - sind Python-Formeln die erhalten bleiben müssen!
    Dim dataRangeNames As Variant
    dataRangeNames = Array("SourceRegion", "ToDoRegion", "DestinationRegion")
    
    Dim rangeName As Variant
    For Each rangeName In dataRangeNames
        On Error Resume Next
        ThisWorkbook.names(CStr(rangeName)).Delete
        On Error GoTo 0
    Next rangeName
End Sub

' ===== BUSY-GUARD: Verhindert gleichzeitige Ausführung mehrerer Operationen =====
' Setzt "Busy"-Status. User kann weiterhin Sheets wechseln/navigieren.
' Schutz: Buttons sind versteckt + gBusy verhindert Re-Entry.
' Return: True wenn erfolgreich in Busy-Modus gewechselt, False wenn bereits busy
' Verwendung: If Not EnterBusy() Then Exit Sub
Private Function EnterBusy() As Boolean
    ' Prüfung: Ist bereits eine Operation aktiv?
    If gBusy > 0 Then
        MsgBox "A process is still running. Please wait until it finishes." & vbCrLf & vbCrLf & _
               "Watch the StatusBar (bottom left) for progress.", _
               vbInformation, "Please Wait"
        Exit Function  ' Ja -> Abbruch, keine Reentrancy erlaubt
    End If
    
    ' Setze Busy-Flag (verhindert dass andere Buttons starten)
    gBusy = 1
    
    ' Application.EnableEvents = False
    ' -> Verhindert Event-Kaskaden (z.B. Worksheet_Change während Import)
    ' -> Wichtig: Events können zu unerwarteten Nebeneffekten führen
    Application.EnableEvents = False
    
    ' KEIN Application.Interactive = False!
    ' User soll während der Berechnung Sheets wechseln / navigieren können.
    ' Schutz gegen Doppelklick: Buttons versteckt + gBusy-Flag.
    
    ' KEIN Application.Cursor = xlWait!
    ' Sanduhr verhindert Sheet-Navigation. StatusBar zeigt Fortschritt.
    
    ' Erfolg: Busy-Modus aktiviert
    EnterBusy = True
End Function

' Beendet Busy-Modus und stellt normale Excel-Interaktivität wieder her
' WICHTIG: Muss IMMER nach EnterBusy() aufgerufen werden (auch bei Fehlern!)
' Typisches Pattern: On Error GoTo CleanFail ... CleanUp: ExitBusy
Private Sub ExitBusy()
    ' Busy-Flag zurücksetzen (andere Buttons können wieder starten)
    If gBusy > 0 Then gBusy = 0
    
    ' Events wieder aktivieren
    Application.EnableEvents = True
End Sub

' Wartet bis Named Range bereit ist (max timeout Sekunden)
' Prüft ob Region existiert und Header-Zeile Daten hat
' Return: True wenn bereit, False wenn Timeout
Private Function WaitForNamedRangeReady(ByVal rangeName As String, Optional ByVal timeoutSec As Double = 10) As Boolean
    Dim checkStart As Double: checkStart = Timer
    Dim testRange As Range
    
    Do While Timer - checkStart < timeoutSec
        Sleep 100  ' 100ms zwischen Checks (CPU-freundlich)
        DoEvents
        
        ' Prüfe ob Named Range bereit ist
        On Error Resume Next
        Set testRange = Nothing
        Set testRange = ThisWorkbook.Names(rangeName).RefersToRange
        If Not testRange Is Nothing Then
            ' Prüfe ob Header-Zeile Daten hat (= Bereich ist komplett)
            If Application.CountA(testRange.Rows(1)) > 0 Then
                On Error GoTo 0
                WaitForNamedRangeReady = True
                Exit Function
            End If
        End If
        On Error GoTo 0
    Loop
    
    ' Timeout erreicht
    WaitForNamedRangeReady = False
End Function

'==================== Helpers ====================
' Wartet bis Python-Zelle einen Wert hat (kein Fehler, kein CALC!)
' Timeout nach 8 Sekunden (Standard)
' Verwendet Sleep(50ms) statt DoEvents für CPU-freundliches Warten
Private Function WaitForPyReady(r As Range, Optional timeoutSec As Double = 8) As Boolean
    Dim t As Double: t = Timer
    Do
        Sleep 50  ' 50ms warten ohne CPU-Last (besser als DoEvents)
        ' DoEvents würde Events pumpen und Race Conditions ermöglichen
        Dim v As Variant: v = r.Value
        If VarType(v) = vbString Then
            If Len(Trim$(CStr(v))) > 0 Then WaitForPyReady = True: Exit Function
        ElseIf Not IsError(v) Then
            WaitForPyReady = True: Exit Function
        End If
        If Timer - t > timeoutSec Then Exit Function
    Loop
End Function

' ===== NICHT-BLOCKIERENDES WARTEN =====
' Sleep blockiert den gesamten Excel-Thread! Während Sleep läuft, kann Excel
' keine Python-Ergebnisse verarbeiten → Berechnungen dauern ewig.
' PumpWait nutzt stattdessen DoEvents in einer Schleife: Excel kann
' zwischendurch Python-Ergebnisse empfangen und verarbeiten.
Private Sub PumpWait(ByVal ms As Long)
    Dim endTime As Double
    endTime = Timer + (ms / 1000#)
    Do While Timer < endTime
        DoEvents
        Sleep 50  ' Nur 50ms blockieren, dann sofort DoEvents
    Loop
End Sub

' ===== SICHERE STATUSBAR-AKTUALISIERUNG =====
' Application.StatusBar kann fehlschlagen (Laufzeitfehler 1004) wenn Excel
' mitten in einer Berechnung ist oder die UI blockiert.
' Diese Helper-Sub fängt den Fehler ab und ignoriert ihn.
Private Sub SafeStatusBar(ByVal msg As Variant)
    On Error Resume Next
    Application.StatusBar = msg
    On Error GoTo 0
End Sub

' ===== POLLING MIT STATUSBAR-FEEDBACK =====
' Prüft NUR die spezifische Zelle, NICHT den globalen CalculationState!
' Problem vorher: CalculationState = xlDone bedeutet ALLE Zellen fertig.
' Wenn PartA im Hintergrund rechnet, blockiert das PartB unnötig.
'
' Lösung: seenBusy-Flag-Ansatz:
'   1) Nach r.Calculate() zeigt die Zelle kurz den ALTEN Wert (stale)
'   2) Dann wechselt sie zu #BUSY!/Error (Python startet)
'   3) Dann kommt der NEUE Wert
' Wir akzeptieren Werte NUR wenn:
'   a) seenBusy=True: Zelle war busy → neuer Wert ist garantiert frisch
'   b) CalculationState=xlDone: ALLES fertig → kein stale möglich (Beschleuniger)
'   c) elapsed > 5s: Fallback falls Python so schnell war dass wir busy verpasst haben
' CalculationState wird NIE als Blockade benutzt, nur als Beschleuniger!
Private Function PollPyCellWithFeedback(ByVal r As Range, ByVal stepLabel As String, ByVal timeoutSec As Double) As Boolean
    Dim startTime As Double: startTime = Timer
    Dim elapsed As Double
    Dim v As Variant
    Dim dotCount As Long: dotCount = 0
    Dim dots As String
    Dim seenBusy As Boolean: seenBusy = False
    Dim errorCount As Long: errorCount = 0
    Const MAX_ERROR_CHECKS As Long = 60  ' 30s bei 500ms = permanenter Fehler
    
    SafeStatusBar stepLabel & ": Python is calculating... Please wait."
    
    Do
        PumpWait 500
        
        elapsed = Timer - startTime
        If elapsed < 0 Then elapsed = elapsed + 86400
        
        dotCount = (dotCount + 1) Mod 4
        dots = String(dotCount + 1, ".")
        
        ' r.Value lesen. On Error Resume Next fängt 2051 ab wenn Excel
        ' global rechnet. v behält dann seinen alten Wert (Empty beim ersten
        ' Mal → IsEmpty setzt seenBusy=True → schnelle Erkennung wenn fertig).
        On Error Resume Next
        v = r.Value
        On Error GoTo 0
        
        If IsError(v) Then
            ' Zelle zeigt Fehler (#BUSY!, #CALC!, #VALUE! etc.)
            ' → Python rechnet noch ODER permanenter Fehler
            seenBusy = True
            errorCount = errorCount + 1
            
            ' Permanenter Fehler? Zwei Stufen:
            ' 1) Quick: 30s Fehler + CalculationState=xlDone → definitiv permanent
            '    (Excel ist fertig, Zelle hat trotzdem Fehler)
            ' 2) Fallback: 90s Fehler unabhängig von CalculationState
            '    (CalculationState bleibt evtl. nie xlDone weil andere Zellen
            '     wie PartB/C permanente Fehler haben)
            If errorCount >= MAX_ERROR_CHECKS And Application.CalculationState = xlDone Then
                SafeStatusBar stepLabel & ": Completed with error. (" & Int(elapsed) & "s)"
                PollPyCellWithFeedback = True
                Exit Function
            ElseIf errorCount >= MAX_ERROR_CHECKS * 3 Then
                SafeStatusBar stepLabel & ": Completed with error. (" & Int(elapsed) & "s)"
                PollPyCellWithFeedback = True
                Exit Function
            End If
            
            SafeStatusBar stepLabel & ": Calculating" & dots & _
                " (" & Int(elapsed) & "s / max " & Int(timeoutSec) & "s)"
        
        ElseIf IsEmpty(v) Then
            ' Leere Zelle: Python wurde gerade gestartet, alte Werte gelöscht
            seenBusy = True
            errorCount = 0
            SafeStatusBar stepLabel & ": Waiting for Python" & dots & _
                " (" & Int(elapsed) & "s / max " & Int(timeoutSec) & "s)"
        
        ElseIf VarType(v) = vbString Then
            Dim sv As String: sv = Trim$(CStr(v))
            If Len(sv) = 0 Then
                ' Leerer String
                seenBusy = True
                errorCount = 0
            ElseIf InStr(1, sv, "CALC", vbTextCompare) > 0 Or _
                   InStr(1, sv, "BUSY", vbTextCompare) > 0 Then
                ' CALC/BUSY Platzhalter
                seenBusy = True
                errorCount = 0
                SafeStatusBar stepLabel & ": Calculating" & dots & _
                    " (" & Int(elapsed) & "s / max " & Int(timeoutSec) & "s)"
            Else
                ' Gültiger String-Wert → Ergebnis-Kandidat
                errorCount = 0
                If seenBusy Then
                    ' Phase 1 bestanden: Zelle WAR busy → dies ist das NEUE Ergebnis
                    SafeStatusBar stepLabel & ": Complete! (" & Int(elapsed) & "s)"
                    PollPyCellWithFeedback = True
                    Exit Function
                ElseIf Application.CalculationState = xlDone Then
                    ' Beschleuniger: ALLES ist fertig → kein stale möglich
                    SafeStatusBar stepLabel & ": Complete! (" & Int(elapsed) & "s)"
                    PollPyCellWithFeedback = True
                    Exit Function
                ElseIf elapsed > 5 Then
                    ' Fallback: 5s vergangen, Python war evtl. zu schnell für busy-Erkennung
                    SafeStatusBar stepLabel & ": Complete! (" & Int(elapsed) & "s)"
                    PollPyCellWithFeedback = True
                    Exit Function
                Else
                    ' Könnte noch stale sein, warten auf busy oder 5s
                    SafeStatusBar stepLabel & ": Verifying" & dots
                End If
            End If
        
        Else
            ' Non-string, non-error, non-empty (DataFrame Spill, Zahl etc.)
            errorCount = 0
            If seenBusy Then
                SafeStatusBar stepLabel & ": Complete! (" & Int(elapsed) & "s)"
                PollPyCellWithFeedback = True
                Exit Function
            ElseIf Application.CalculationState = xlDone Then
                SafeStatusBar stepLabel & ": Complete! (" & Int(elapsed) & "s)"
                PollPyCellWithFeedback = True
                Exit Function
            ElseIf elapsed > 5 Then
                SafeStatusBar stepLabel & ": Complete! (" & Int(elapsed) & "s)"
                PollPyCellWithFeedback = True
                Exit Function
            Else
                SafeStatusBar stepLabel & ": Verifying" & dots
            End If
        End If
        
        ' Timeout-Prüfung
        If elapsed > timeoutSec Then
            SafeStatusBar stepLabel & ": TIMEOUT after " & Int(elapsed) & "s!"
            PollPyCellWithFeedback = False
            Exit Function
        End If
    Loop
End Function

' ===== DYNAMISCHER TIMEOUT BASIEREND AUF DATENMENGE =====
' Berechnet sinnvollen Timeout abhängig von der Zeilenanzahl.
' Formel: base + (rows * perRow), geclampt auf [minSec, maxSec]
' Standard: 30s Basis + 0.5s pro Zeile, min 30s, max 300s (5 Minuten)
Private Function CalculateDynamicTimeout( _
        ByVal rowCount As Long, _
        Optional ByVal baseSeconds As Double = 30, _
        Optional ByVal perRowSeconds As Double = 0.5, _
        Optional ByVal minSeconds As Double = 45, _
        Optional ByVal maxSeconds As Double = 600) As Double
    Dim result As Double
    result = baseSeconds + (rowCount * perRowSeconds)
    If result < minSeconds Then result = minSeconds
    If result > maxSeconds Then result = maxSeconds
    CalculateDynamicTimeout = result
End Function

' ===== PRÜFT OB EINE PYTHON-ZELLE NOCH AKTIV BERECHNET =====
' Rein zell-basierte Prüfung, KEIN globaler CalculationState!
' Prüft: Zellwert (Error/Empty/CALC/BUSY) + Spill-Range auf Fehler.
' Return: True wenn Zelle noch beschäftigt aussieht, False wenn fertig.
Private Function IsPyCellBusy(ByVal r As Range) As Boolean
    Dim v As Variant
    On Error Resume Next
    v = r.Value
    On Error GoTo 0
    
    ' Fehler in der Zelle (#BUSY!, #CALC!, #VALUE! etc.) → busy
    If IsError(v) Then
        IsPyCellBusy = True
        Exit Function
    End If
    
    ' Leere Zelle → busy (Python hat noch kein Ergebnis)
    If IsEmpty(v) Then
        IsPyCellBusy = True
        Exit Function
    End If
    
    ' String mit CALC/BUSY → busy
    If VarType(v) = vbString Then
        Dim sv As String: sv = UCase$(Trim$(CStr(v)))
        If Len(sv) = 0 Or InStr(sv, "BUSY") > 0 Or InStr(sv, "CALC") > 0 Then
            IsPyCellBusy = True
            Exit Function
        End If
    End If
    
    ' Prüfe Spill-Range auf Fehler (Busy-Icons in Spill-Bereich)
    Dim spill As Range
    On Error Resume Next
    Set spill = r.SpillingToRange
    On Error GoTo 0
    If Not spill Is Nothing Then
        If spill.Cells.Count > 1 Then
            Dim cv As Variant
            cv = spill.Cells(2, 1).Value
            If IsError(cv) Then
                IsPyCellBusy = True
                Exit Function
            End If
        End If
    End If
    
    IsPyCellBusy = False
End Function

' ===== WARTET BIS ALLE PYTHON-ZELLEN FERTIG GERECHNET HABEN =====
' Wartet NUR auf Application.CalculationState = xlDone (globaler Zustand).
' Prüft NICHT einzelne Zellwerte! Grund: Nach dem Import haben PartB/PartC
' permanente Fehler (#VALUE!) weil ihre Inputs (ToDoRegion) noch nicht existieren.
' IsPyCellBusy würde diese Fehler als "busy" interpretieren → Endlosschleife.
' 2x stable-Check: Erst wenn 2x hintereinander xlDone, gilt es als settled.
' Return: True wenn fertig, False wenn Timeout
Private Function WaitForAllPySettled( _
        Optional ByVal stepLabel As String = "Settling", _
        Optional ByVal timeoutSec As Double = 180) As Boolean
    
    Dim startTime As Double: startTime = Timer
    Dim elapsed As Double
    Dim dotCount As Long: dotCount = 0
    Dim dots As String
    Dim stableCount As Long: stableCount = 0
    
    ' Schnell-Check: vielleicht ist schon alles fertig
    If Application.CalculationState = xlDone Then
        ' Einmal kurz warten und nochmal prüfen (2x stable)
        PumpWait 500
        If Application.CalculationState = xlDone Then
            WaitForAllPySettled = True
            Exit Function
        End If
    End If
    
    SafeStatusBar stepLabel & ": Waiting for Python calculations to finish..."
    
    Do
        PumpWait 500
        
        elapsed = Timer - startTime
        If elapsed < 0 Then elapsed = elapsed + 86400
        
        dotCount = (dotCount + 1) Mod 4
        dots = String(dotCount + 1, ".")
        
        If Application.CalculationState = xlDone Then
            stableCount = stableCount + 1
            If stableCount >= 2 Then
                SafeStatusBar stepLabel & ": All calculations done. (" & Int(elapsed) & "s)"
                PumpWait 500
                SafeStatusBar False
                WaitForAllPySettled = True
                Exit Function
            Else
                SafeStatusBar stepLabel & ": Confirming..." & dots & _
                    " (" & Int(elapsed) & "s)"
            End If
        Else
            stableCount = 0
            SafeStatusBar stepLabel & ": Calculating" & dots & _
                " (" & Int(elapsed) & "s / max " & Int(timeoutSec) & "s)"
        End If
        
        ' Timeout
        If elapsed > timeoutSec Then
            SafeStatusBar stepLabel & ": TIMEOUT after " & Int(elapsed) & "s!"
            PumpWait 1000
            SafeStatusBar False
            WaitForAllPySettled = False
            Exit Function
        End If
    Loop
End Function

' Führt Python in Excel Formeln aus (PartA, PartB, PartC)
' Parameter:
'   names      - Array mit Named Range Namen (z.B. Array("PartA"))
'   stepLabel  - Anzeigename für StatusBar-Feedback (z.B. "Step 2: PartA")
'   timeoutSec - Max. Wartezeit in Sekunden (Standard 120s, dynamisch berechnen!)
'
' Architektur:
'   1) Sicherstellt xlCalculationAutomatic (Python braucht es!)
'   2) r.Calculate erzwingt Neuberechnung der spezifischen Zelle
'   3) PollPyCellWithFeedback wartet per seenBusy-Flag auf das Ergebnis
'      → prüft NUR die Zelle, NICHT globalen CalculationState als Blockade
'      → andere Python-Zellen dürfen parallel rechnen ohne zu stören
Private Sub RunPyNamed(names As Variant, _
        Optional ByVal stepLabel As String = "Python", _
        Optional ByVal timeoutSec As Double = 120)
    Dim nm As Variant, r As Range
    
    ' Python in Excel braucht xlCalculationAutomatic (sonst durchgestrichene Zellen)
    If Application.Calculation <> xlCalculationAutomatic Then
        Application.Calculation = xlCalculationAutomatic
    End If
    Application.ScreenUpdating = False
    
    For Each nm In names
        Set r = ThisWorkbook.names(CStr(nm)).RefersToRange
        
        SafeStatusBar stepLabel & ": Starting..."
        
        ' r.Calculate erzwingt Neuberechnung dieser Zelle.
        ' Wenn CalculationState <> xlDone (andere Zellen rechnen noch),
        ' wirft r.Calculate Error 2051. Deshalb: kurze Retry-Schleife.
        ' WICHTIG: r.Calculate MUSS aufgerufen werden! Ohne das wird z.B.
        ' PartB nicht mit dem neuen ToDoRegion berechnet (Auto-Calc erkennt
        ' Änderungen an Named Ranges nicht zuverlässig).
        Dim calcRetry As Long
        For calcRetry = 1 To 10  ' Max 10 × 1s = 10s
            On Error Resume Next
            r.Calculate
            If Err.Number = 0 Then
                On Error GoTo 0
                Exit For
            End If
            On Error GoTo 0
            PumpWait 1000
            SafeStatusBar stepLabel & ": Waiting for Excel... (" & calcRetry & "s)"
        Next calcRetry
        DoEvents
        
        ' Polling mit zell-basiertem Feedback (kein CalculationState-Gate!)
        If Not PollPyCellWithFeedback(r, stepLabel, timeoutSec) Then
            SafeStatusBar False
            Application.ScreenUpdating = True
            Err.Raise vbObjectError + 5001, "RunPyNamed", _
                "Timeout: Calculation not completed after " & _
                Int(timeoutSec) & " seconds." & vbCrLf & vbCrLf & _
                "The source data may be very large. Please try again." & vbCrLf & _
                "Watch the StatusBar (bottom left) for progress."
        End If
    Next nm
    SafeStatusBar False
    Application.ScreenUpdating = True
End Sub

' ===== SHEET-EXISTENZ-PRÜFUNG: Erstellt Sheet falls nicht vorhanden =====
' Verwendet in: Run_PartA_To_ToDo(), Run_PartC_To_Destination(), ImportSourceFromXlsx()
' Beispiel: EnsureSheet("ToDo (User)") -> gibt Worksheet-Objekt zurück
' Verhindert Fehler wenn Sheet noch nicht existiert (z.B. nach Clear_DataSheets)
Private Function EnsureSheet(ByVal sheetName As String) As Worksheet
    Dim ws As Worksheet
    
    ' Versuche Sheet zu finden (ignoriere Fehler falls nicht vorhanden)
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(sheetName)  ' Suche nach Sheet-Name
    On Error GoTo 0  ' Fehlerbehandlung zurücksetzen
    
    ' Wurde Sheet gefunden?
    If ws Is Nothing Then
        ' Nein -> Sheet existiert nicht, neu erstellen
        ' Add(After:=...Count) -> Fügt Sheet am Ende ein (nicht am Anfang)
        Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
        ws.Name = sheetName  ' Benenne Sheet um (z.B. "Sheet1" -> "ToDo (User)")
    End If
    
    ' Return: Worksheet-Objekt (entweder gefunden oder neu erstellt)
    Set EnsureSheet = ws
End Function

' Erstellt/aktualisiert einen Workbook-globalen Named Range
' Verwendet für: SourceRegion, ToDoRegion, DestinationRegion
' EINFACHE METHODE: Direkt Range-Objekt übergeben (Excel erstellt interne Referenz)
' Python-Skripte können mit xl("SourceRegion") darauf zugreifen
Private Sub SetNamedRange(ByVal nameText As String, ByVal Target As Range)
    On Error Resume Next
    ThisWorkbook.Names(nameText).Delete  ' Alte Range löschen (falls vorhanden)
    On Error GoTo 0
    
    ' DIREKTE Zuweisung: Excel erstellt automatisch korrekte Referenz
    ThisWorkbook.Names.Add Name:=nameText, RefersTo:=Target
End Sub

' ===== NAMED RANGE EXISTENZ-PRÜFUNG =====
' Prüft ob ein Named Range existiert (z.B. "SourceRegion", "ToDoRegion", "DestinationRegion")
' Verwendet in: Run_PartA_To_ToDo(), Run_PartB_Validations(), Run_PartC_To_Destination(), Run_PartD_Export()
Private Function NameNotExists(ByVal nm As String) As Boolean
    On Error Resume Next  ' Fehler ignorieren wenn Name nicht existiert
    Dim r As Range: Set r = ThisWorkbook.names(nm).RefersToRange
    NameNotExists = (r Is Nothing)  ' True wenn Range = Nothing (nicht gefunden)
    ' Note: On Error Resume Next bleibt aktiv, aber wird durch nächstes On Error GoTo 0 zurückgesetzt
End Function

' Holt den Spill-Bereich einer Python in Excel Zelle
' Python-Zellen geben DataFrame zurück -> "Spill" in benachbarte Zellen
' WICHTIG: Python-Zelle muss auf "Excel Value" eingestellt sein (nicht Python Object!)
' 1) Versuche SpillingToRange (native Excel Spill-Erkennung)
' 2) Fallback: Manuell Rechteck erkennen (Header bis erste Leerzeile)
Private Function GetSourceSpillRange(srcTop As Range) As Range
    Dim spill As Range
    On Error Resume Next
    Set spill = srcTop.SpillingToRange  ' Excel's native Spill-Range Erkennung
    On Error GoTo 0
    If Not spill Is Nothing Then
        Set GetSourceSpillRange = spill
        Exit Function
    End If

    ' Fallback: Manuelles Erkennen des Rechtecks ab Header bis erste Leerzeile
    ' Wird verwendet wenn SpillingToRange nicht verfügbar ist
    Dim ws As Worksheet: Set ws = srcTop.Parent
    Dim nCols As Long, curRow As Long, emptyRow As Boolean, c As Range
    Dim MAX_ROWS As Long: MAX_ROWS = 200000

    nCols = 0
    For Each c In ws.Range(srcTop, ws.Cells(srcTop.Row, ws.Columns.Count))
        If Len(Trim$(CStr(c.Value))) = 0 Then Exit For
        nCols = nCols + 1
    Next c
    If nCols = 0 Then nCols = 1

    curRow = srcTop.Row + 1
    Do
        If curRow - srcTop.Row > MAX_ROWS Then Exit Do
        emptyRow = Application.CountA(ws.Range(ws.Cells(curRow, srcTop.Column), ws.Cells(curRow, srcTop.Column + nCols - 1))) = 0
        If emptyRow Then Exit Do
        curRow = curRow + 1
    Loop

    If curRow <= srcTop.Row Then curRow = srcTop.Row + 1
    Set GetSourceSpillRange = ws.Range(srcTop, ws.Cells(curRow - 1, srcTop.Column + nCols - 1))
End Function

' Kopiert Python-Spill-Ergebnis als Werte (ohne Formeln) in Ziel-Sheet
' Formatiert als Text (@) um "000" -> "0" Konvertierung zu vermeiden
' DocPart "000" würde ohne Text-Format zu "0" werden
' Zwei Methoden:
'   1) Normal: Copy -> PasteSpecial -> Text-Format
'   2) Fallback: Zelle-für-Zelle Kopie mit CStr() wenn Fehler auftreten
Private Sub CopyValuesAsValues_Paste(src As Range, dstTopLeft As Range)
    On Error GoTo SimpleFallback
    
    ' Versuche normale Copy-Paste zuerst
    src.Copy
    dstTopLeft.PasteSpecial Paste:=xlPasteValues
    Application.CutCopyMode = False
    
    ' Text-Formatierung für String-Erhaltung
    ' @ = Text-Format verhindert automatische Excel-Konvertierung
    Dim dstRange As Range
    Set dstRange = dstTopLeft.Resize(src.rows.Count, src.Columns.Count)
    dstRange.NumberFormat = "@"
    
    Exit Sub
    
SimpleFallback:
    ' Bei Fehlern: Einfache Zelle-für-Zelle Kopie
    Application.CutCopyMode = False
    Dim i As Long, j As Long
    For i = 1 To src.rows.Count
        For j = 1 To src.Columns.Count
            On Error Resume Next
            dstTopLeft.Offset(i - 1, j - 1).NumberFormat = "@"
            dstTopLeft.Offset(i - 1, j - 1).Value = CStr(src.Cells(i, j).Value)
            On Error GoTo 0
        Next j
    Next i
End Sub

' ===== IMPORT-BUTTON: Startet kompletten Import-Workflow =====
' Button: "Excel-Datei laden"
' Workflow: ImportSourceFromXlsx erstellt SourceRegion und setzt Calculation Mode
' WICHTIG: showMsg:=False verhindert doppelte MessageBoxen
' WICHTIG: Kurze Wartezeit nach Import damit Excel Daten verarbeiten kann
Public Sub Load_ExcelButton()
    On Error GoTo CleanFail
    
    ' WICHTIG: ThisWorkbook aktivieren BEVOR Buttons versteckt werden
    ThisWorkbook.Activate
    Application.ScreenUpdating = True
    DisableAllButtons  ' Alle Buttons verstecken während Import
    DoEvents
    
    ' ImportSourceFromXlsx erledigt alles: Import + SourceRegion erstellen
    ImportSourceFromXlsx showMsg:=False
    
    ' Prüfe ob Import erfolgreich war (SourceRegion existiert)
    On Error Resume Next
    Dim checkRegion As Range
    Set checkRegion = ThisWorkbook.Names("SourceRegion").RefersToRange
    On Error GoTo 0
    
    ' Wenn kein Import (User hat abgebrochen):
    ' Python-Zellen rechnen kurz mit fehlenden Inputs (2-3s) → Error-DataFrame.
    ' Warte kurz damit Busy-Icons verschwinden bevor Buttons wieder erscheinen.
    If checkRegion Is Nothing Then
        SafeStatusBar "Import cancelled. Waiting for Python to settle..."
        Dim cancelSettleStart As Double: cancelSettleStart = Timer
        Dim cancelElapsed As Double
        Do
            PumpWait 500
            cancelElapsed = Timer - cancelSettleStart
            If cancelElapsed < 0 Then cancelElapsed = cancelElapsed + 86400
            If Application.CalculationState = xlDone Then Exit Do
            If cancelElapsed > 10 Then Exit Do  ' Max 10s warten
        Loop
        SafeStatusBar False
        GoTo CleanUp
    End If
    
    ' Config-Sheet initialisieren
    InitializeConfigSheet
    
    ' Config-Werte in versteckte Zellen schreiben (für Python-Zugriff)
    Dim configSheet As Worksheet
    On Error Resume Next
    Set configSheet = ThisWorkbook.Worksheets("_Config")
    On Error GoTo 0
    
    If Not configSheet Is Nothing Then
        ' Schreibe Config-Flags in Zellen F1-F10 (Python kann diese lesen)
        configSheet.Range("F1").Value = GetConfigValue("ApplyPrintingGoodRule")
        configSheet.Range("F2").Value = GetConfigValue("FilterQepDrwDocTypes")
        configSheet.Range("F3").Value = GetConfigValue("ExportPath")
    End If
    
    ' xlCalculationAutomatic setzen + Application.Calculate um Berechnung zu starten.
    ' Application.Calculate ist NÖTIG nach dem Wechsel von xlCalculationManual.
    Application.Calculation = xlCalculationAutomatic
    Application.Calculate
    DoEvents
    
    ' ASYNC WARTEN per Application.OnTime.
    ' JEDE VBA-Schleife (Sleep, DoEvents, PumpWait) blockiert den Excel-Thread
    ' und verhindert dass Python-Ergebnisse verarbeitet werden.
    ' Application.OnTime beendet VBA KOMPLETT → Excel rechnet frei →
    ' nach 1s prüft ImportCheckDone ob fertig.
    mImportRows = checkRegion.Rows.Count - 1
    mImportStart = Timer
    SafeStatusBar "Import done. Processing data (" & mImportRows & " rows)..."
    Application.OnTime Now + TimeSerial(0, 0, 1), "ImportCheckDone"
    ' KEIN CleanUp hier! Das macht ImportCheckDone.
    Exit Sub
    
CleanUp:
    EnableAllButtons
    SafeStatusBar False
    DoEvents
    Exit Sub

CleanFail:
    On Error Resume Next
    SafeStatusBar False
    On Error GoTo 0
    EnableAllButtons
    If Err.Number <> 0 Then
        MsgBox "Error during import workflow: " & Err.Description, vbCritical, "Import Error"
    End If
    Resume CleanUp
End Sub

' ===== ASYNC IMPORT CALLBACK =====
' Wird per Application.OnTime aufgerufen, 1s nach Application.Calculate.
' VBA ist komplett beendet → Excel kann Python-Ergebnisse frei verarbeiten.
' Prüft CalculationState: fertig → MsgBox + Buttons. Nicht fertig → nochmal 1s warten.
Public Sub ImportCheckDone()
    On Error Resume Next  ' Sicherheit falls Workbook geschlossen wurde
    
    Dim elapsed As Double
    elapsed = Timer - mImportStart
    If elapsed < 0 Then elapsed = elapsed + 86400
    
    If Application.CalculationState = xlDone Then
        ' Fertig! Erfolgs-Meldung zeigen
        SafeStatusBar False
        MsgBox "Import successful! " & mImportRows & " rows imported.", _
               vbInformation, "Import Complete"
        EnableAllButtons
        DoEvents
    ElseIf elapsed > CalculateDynamicTimeout(mImportRows) Then
        ' Timeout: Trotzdem weitermachen
        SafeStatusBar False
        MsgBox "Import successful! " & mImportRows & " rows imported." & vbCrLf & vbCrLf & _
               "Data processing is still running." & vbCrLf & _
               "Please wait a moment, then click the next button.", _
               vbExclamation, "Import Complete"
        EnableAllButtons
        DoEvents
    Else
        ' Noch nicht fertig → in 1s nochmal prüfen
        SafeStatusBar "Import: Processing data... (" & Int(elapsed) & "s)"
        Application.OnTime Now + TimeSerial(0, 0, 1), "ImportCheckDone"
    End If
    
    On Error GoTo 0
End Sub

' ===== WORKBOOK OPEN EVENT: Automatischer Import beim Öffnen =====
' Wird in Workbook_Open() in 'Diese Arbeitsmappe' aufgerufen
' Nutzt denselben Workflow wie der Import-Button (Load_ExcelButton).
Public Sub Init_ImportOnOpen()
    Load_ExcelButton
End Sub

' ===== REFRESH-BUTTON: Aktualisiert SourceRegion ohne neuen Import =====
' Button: "Quelle aktualisieren"
' Verwendet wenn: Source-Daten manuell geändert wurden
' Aktualisiert nur CurrentRegion-Bereich, KEIN neuer Import
Public Sub Refresh_SourceRegion()
    UpdateSourceRegion                    ' Aktualisiere Bereich
    MsgBox "Source updated.", vbInformation  ' Bestätigung
End Sub

' Aktualisiert SourceRegion Named Range auf den aktuellen Datenbereich.
' KEIN Application.Calculate: Python-Zellen werden NUR über Button-Klicks
' (RunPyNamed) berechnet, nicht automatisch.
' Verwendet in: Load_ExcelButton(), Init_ImportOnOpen(), Refresh_SourceRegion()
Public Sub UpdateSourceRegion()
    Dim ws As Worksheet, rng As Range
    
    ' Versuche "source" Sheet zu finden (ignoriere Fehler falls nicht vorhanden)
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets("source")
    On Error GoTo 0  ' Fehlerbehandlung zurücksetzen
    If ws Is Nothing Then Exit Sub  ' Sheet existiert nicht -> Abbruch
    
    ' Hole CurrentRegion ab A1 (automatische Datenbereich-Erkennung)
    On Error Resume Next
    Set rng = ws.Range("A1").CurrentRegion  ' Zusammenhängender Bereich
    On Error GoTo 0
    If rng Is Nothing Then Exit Sub  ' Kein Datenbereich gefunden -> Abbruch
    
    ' Erstelle/aktualisiere Named Range mit aktuellem Datenbereich
    SetNamedRange "SourceRegion", rng
End Sub

'==================== Buttons A–D ====================
' A) Holt die transformierte Tabelle aus PartA (Python Zelle) und fügt sie in "ToDo (User)" ein.
Public Sub Run_PartA_To_ToDo()

    If Not EnterBusy() Then Exit Sub
    On Error GoTo CleanFail
    
    ' Check if SourceRegion exists
    If NameNotExists("SourceRegion") Then
        MsgBox "Error: No source data found!" & vbCrLf & _
               "Please run Import (Step 1) first.", vbExclamation, "No Data"
        GoTo CleanUp
    End If
    
    ' WICHTIG: Prüfe ob PartA Named Range existiert
    If NameNotExists("PartA") Then
        MsgBox "Error: PartA formula not found!" & vbCrLf & vbCrLf & _
               "Please create a Python in Excel cell and name it 'PartA'." & vbCrLf & _
               "The formula should process SourceRegion and return a DataFrame." & vbCrLf & vbCrLf & _
               "Instructions:" & vbCrLf & _
               "1. Create Python cell with formula from PartA_paste.txt" & vbCrLf & _
               "2. Select the cell" & vbCrLf & _
               "3. In Name Box (left of formula bar) type: PartA" & vbCrLf & _
               "4. Press Enter", vbExclamation, "PartA Setup Required"
        GoTo CleanUp
    End If
    
    ' Deaktiviere alle Buttons während Python-Berechnung
    DisableAllButtons
    DoEvents
    
    ' ===== DYNAMISCHER TIMEOUT basierend auf Datenmenge =====
    Dim srcRegion As Range
    Set srcRegion = ThisWorkbook.Names("SourceRegion").RefersToRange
    Dim srcRowCount As Long: srcRowCount = srcRegion.Rows.Count - 1  ' minus Header
    Dim pyTimeout As Double: pyTimeout = CalculateDynamicTimeout(srcRowCount)
    
    ' A) Python laufen lassen MIT StatusBar-Feedback
    RunPyNamed Array("PartA"), "Step 2: Creating ToDo table", pyTimeout

    Dim srcTop As Range: Set srcTop = ThisWorkbook.names("PartA").RefersToRange
    
    ' ===== PRÜFUNG: Ist Python fertig? =====
    ' RunPyNamed hat bereits mit Feedback gewartet.
    ' Hier nur noch zur Sicherheit den Rückgabewert prüfen.
    Dim topValue As Variant: topValue = srcTop.Value
    
    If IsError(topValue) Then
        MsgBox "Error: Python calculation failed." & vbCrLf & _
               "Error: " & CStr(topValue), vbCritical, "Calculation Error"
        GoTo CleanUp
    ElseIf InStr(1, CStr(topValue), "CALC", vbTextCompare) > 0 Then
        MsgBox "Error: Calculation not yet complete." & vbCrLf & _
               "Python needed more time than expected (" & Int(pyTimeout) & "s timeout)." & vbCrLf & vbCrLf & _
               "Tip: Check under 'Formulas' > 'Calculation Options' that 'Automatic' is selected.", _
               vbExclamation, "Calculation Pending"
        GoTo CleanUp
    End If
    ' Erfolg -> Fortfahren mit Spill-Range holen
    
    Dim src As Range:    Set src = GetSourceSpillRange(srcTop)
    
    ' DEBUGGING: Prüfe ob Spill-Range Daten hat
    If src.Rows.Count <= 1 Then
        MsgBox "ERROR: Processing returned only header, no data rows!" & vbCrLf & vbCrLf & _
               "Spill Range: " & src.Address & vbCrLf & _
               "Rows: " & src.Rows.Count & vbCrLf & _
               "Cols: " & src.Columns.Count & vbCrLf & vbCrLf & _
               "Check if the Python formula is working correctly." & vbCrLf & _
               "Top cell value: " & CStr(srcTop.Value), vbCritical, "No Data"
        GoTo CleanUp
    End If

    Dim wsOut As Worksheet: Set wsOut = EnsureSheet("ToDo (User)")
    CopyValuesAsValues_Paste src, wsOut.Range("A1")

    Dim tgt As Range: Set tgt = wsOut.Range("A1").Resize(src.Rows.Count, src.Columns.Count)
    SetNamedRange "ToDoRegion", tgt

    ' Python ist VERIFIZIERT fertig (PollPyCellWithFeedback hat bestätigt).
    Dim dataRows As Long: dataRows = src.Rows.Count - 1
    
    ' KEIN Application.Calculate hier! Das würde ALLE Python-Zellen
    ' (PartA+B+C) neu starten und den nächsten Step blockieren.
    DoEvents
    
    MsgBox "Step 2 completed: " & dataRows & " data rows transferred to ToDo (User).", _
           vbInformation, "Success"
    
    ' Buttons VERZÖGERT einblenden (3s). SetNamedRange "ToDoRegion" hat
    ' Auto-Calc getriggert → PartB/C rechnen im Hintergrund.
    ' Ohne Delay klickt der User sofort auf Validate → VBA blockiert Excel → Error.
    SafeStatusBar False
    ExitBusy
    EnableAllButtonsDelayed
    Exit Sub

CleanUp:
    SafeStatusBar False
    ExitBusy
    EnableAllButtons
    Exit Sub

CleanFail:
    SafeStatusBar False
    EnableAllButtons
    Resume CleanUp
End Sub

' B) Liest die Tabelle aus "ToDo (User)" (ToDoRegion) und zeigt dem User die Validierungsissues.
Public Sub Run_PartB_Validations()
    ' Prüfe ToDo (User) Sheet direkt (nicht Named Range)
    Dim wsCheck As Worksheet
    On Error Resume Next
    Set wsCheck = ThisWorkbook.Worksheets("ToDo (User)")
    On Error GoTo 0
    
    If wsCheck Is Nothing Then
        MsgBox "Error: Intermediate table 'ToDo (User)' not found!" & vbCrLf & _
               "Please first run Step 1 to create the intermediate table.", vbExclamation, "Table Missing"
        Exit Sub
    End If
    
    ' Prüfe ob überhaupt Daten vorhanden sind (mindestens 2 Zeilen: Header + 1 Datenzeile)
    If Application.CountA(wsCheck.Range("A:A")) <= 1 Then
        MsgBox "Error: Intermediate table is empty!" & vbCrLf & _
               "Please first run Step 1 to process data.", vbExclamation, "No Data"
        Exit Sub
    End If
    
    ' Wenn ToDoRegion existiert, nutze es. Sonst erstelle es neu.
    If NameNotExists("ToDoRegion") Then
        ' ToDoRegion existiert nicht -> erstelle es aus aktuellem Sheet-Inhalt
        On Error Resume Next
        Dim rng As Range
        Set rng = wsCheck.Range("A1").CurrentRegion
        If Not rng Is Nothing Then
            SetNamedRange "ToDoRegion", rng
        End If
        On Error GoTo 0
    End If

    If Not EnterBusy() Then Exit Sub
    On Error GoTo CleanFail
    
    ' Deaktiviere alle Buttons während Validierungs-Berechnung
    DisableAllButtons
    DoEvents

    ' Dynamischer Timeout basierend auf ToDoRegion-Größe
    Dim todoRng As Range
    On Error Resume Next
    Set todoRng = ThisWorkbook.Names("ToDoRegion").RefersToRange
    On Error GoTo CleanFail
    Dim todoRows As Long
    If Not todoRng Is Nothing Then todoRows = todoRng.Rows.Count - 1 Else todoRows = 100
    Dim pyTimeout As Double: pyTimeout = CalculateDynamicTimeout(todoRows, 20, 0.3, 20, 180)
    
    RunPyNamed Array("PartB"), "Step 3: Validating data", pyTimeout
    Dim top As Range: Set top = ThisWorkbook.names("PartB").RefersToRange

    ' Zellwert sicher lesen (könnte noch Error-Variant sein nach Timeout)
    Dim topVal As Variant: topVal = top.Value
    Dim txt As String
    If IsError(topVal) Then
        txt = "Error: Python calculation did not complete. Please try again."
    Else
        txt = CStr(topVal)
    End If
    If Len(Trim$(txt)) = 0 Or LCase$(txt) = "no validation errors found." Then
        MsgBox "No validation errors found.", vbInformation
    Else
        ' Bessere Fehlerbehandlung für Excel-Fehler
        If InStr(LCase$(txt), "error") > 0 And InStr(LCase$(txt), "toda") > 0 Then
            MsgBox txt, vbExclamation, "Data Validation - Problem"
        ElseIf LCase$(Left$(txt, 8)) = "pyerror:" Then
            MsgBox txt, vbCritical, "Validation - System Error"
        Else
            MsgBox txt, vbExclamation, "Data Validation - Found Issues"
        End If
    End If
    
    ' Buttons verzögert aktivieren
    SafeStatusBar False
    ExitBusy
    EnableAllButtonsDelayed
    Exit Sub

CleanUp:
    SafeStatusBar False
    ExitBusy
    EnableAllButtons
    Exit Sub

CleanFail:
    SafeStatusBar False
    EnableAllButtons
    MsgBox "Error during data validation: " & Err.Description, vbCritical, "Validation Error"
    Resume CleanUp
End Sub

' C) Holt die transformierte Tabelle aus PartC und fügt sie in "destination" ein.
Public Sub Run_PartC_To_Destination()
    If NameNotExists("ToDoRegion") Then
        MsgBox "Error: No validated data available!" & vbCrLf & _
               "Please first run data processing (Step 1).", vbExclamation, "Data Processing Required"
        Exit Sub
    End If

    If Not EnterBusy() Then Exit Sub
    On Error GoTo CleanFail
    
    ' Deaktiviere alle Buttons während Python-Berechnung
    DisableAllButtons
    DoEvents
    
    ' Dynamischer Timeout basierend auf ToDoRegion-Größe
    Dim todoRng As Range
    Set todoRng = ThisWorkbook.Names("ToDoRegion").RefersToRange
    Dim todoRows As Long: todoRows = todoRng.Rows.Count - 1
    Dim pyTimeout As Double: pyTimeout = CalculateDynamicTimeout(todoRows)

    RunPyNamed Array("PartC"), "Step 4: Preparing export", pyTimeout

    Dim srcTop As Range: Set srcTop = ThisWorkbook.names("PartC").RefersToRange
    Dim src As Range:   Set src = GetSourceSpillRange(srcTop)

    Dim wsDst As Worksheet: Set wsDst = EnsureSheet("destination")

    CopyValuesAsValues_Paste src, wsDst.Range("A1")

    Dim tgt As Range: Set tgt = wsDst.Range("A1").Resize(src.Rows.Count, src.Columns.Count)
    SetNamedRange "DestinationRegion", tgt

    ' Python ist VERIFIZIERT fertig (PollPyCellWithFeedback hat bestätigt).
    Dim dataRows As Long: dataRows = src.Rows.Count - 1
    
    ' KEIN Application.Calculate hier! Das würde ALLE Python-Zellen
    ' neu starten und den nächsten Step blockieren.
    DoEvents
    
    MsgBox "Step 4 completed: " & dataRows & " rows prepared for export.", _
           vbInformation, "Export Preparation"
    
    SafeStatusBar False
    ExitBusy
    EnableAllButtonsDelayed
    Exit Sub

CleanUp:
    SafeStatusBar False
    ExitBusy
    EnableAllButtons
    Exit Sub

CleanFail:
    SafeStatusBar False
    EnableAllButtons
    Resume CleanUp
End Sub

' D) Export
Public Sub Run_PartD_Export()
    If NameNotExists("DestinationRegion") Then
        MsgBox "Error: No export-ready data available!" & vbCrLf & _
               "Please first prepare data for export (Step 3).", vbExclamation, "Export Preparation Required"
        Exit Sub
    End If
    
    If Not EnterBusy() Then Exit Sub
    On Error GoTo CleanFail
    
    ' Hole Export-Pfad aus Config (Fallback: C:\TEMP)
    InitializeConfigSheet
    Dim exportPath As String
    exportPath = GetConfigValue("ExportPath")
    If Len(Trim(exportPath)) = 0 Then exportPath = "C:\TEMP"
    
    ExportCsvByParent_FromNamed "DestinationRegion", exportPath
    
    ' Kurze Pause damit Datei-Operationen abgeschlossen werden
    PumpWait 500

CleanUp:
    ExitBusy
    EnableAllButtons  ' Stelle sicher dass nach Export alle Buttons sichtbar sind
    Exit Sub

CleanFail:
    ' Bei Fehlern ALLE Buttons wieder sichtbar machen (Failsafe)
    EnableAllButtons
    Resume CleanUp
End Sub

' ===== ENTFERNT S+4-ZEICHEN PRÄFIX AUS PARENT-NAMEN =====
' Verwendet in: ExportCsvByParent_FromNamed (Dateiname-Bereinigung)
' Pattern: "S" + 4 alphanumerische Zeichen (A-Z, 0-9)
' Beispiele: "S1234ABC" -> "ABC", "SXYZA920" -> "920", "ABC" -> "ABC" (unverändert)
' WICHTIG: Nur wenn EXAKT dieses Muster am Anfang steht
Private Function StripS4Prefix(ByVal s As String) As String
    Dim t As String: t = Trim$(CStr(s))  ' Trimme Whitespace
    
    ' Prüfe: Mindestens 5 Zeichen lang UND beginnt mit "S"?
    If Len(t) >= 5 And UCase$(Left$(t, 1)) = "S" Then
        ' Hole die nächsten 4 Zeichen nach dem "S"
        Dim four As String: four = UCase$(Mid$(t, 2, 4))
        
        ' Prüfe: Sind alle 4 Zeichen alphanumerisch (A-Z oder 0-9)?
        ' Like-Pattern: [A-Z0-9] = ein Zeichen aus Bereich
        If four Like "[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]" Then
            StripS4Prefix = Mid$(t, 6)  ' Gib alles NACH den ersten 5 Zeichen zurück
            Exit Function
        End If
    End If
    
    ' Kein Match -> Original-String zurückgeben
    StripS4Prefix = t
End Function

'==================== Export ====================
Private Sub ExportCsvByParent_FromNamed(namedRange As String, outDir As String)
    Dim rng As Range, ws As Worksheet
    Set rng = ThisWorkbook.names(namedRange).RefersToRange
    Set ws = rng.Parent

    Dim header As Range, data As Range
    Set header = rng.rows(1)
    If rng.rows.Count > 1 Then
        Set data = rng.Offset(1, 0).Resize(rng.rows.Count - 1)
    Else
        MsgBox "No data rows available for export.", vbExclamation
        Exit Sub
    End If

    Dim colParent As Long: colParent = FindHeaderColumnInRange(header, "Parent")
    If colParent = 0 Then
        MsgBox "Column 'Parent' not found in range '" & namedRange & "'.", vbCritical
        Exit Sub
    End If
    
    ' Structure Level Spalte finden (optional)
    Dim colStructureLevel As Long: colStructureLevel = FindHeaderColumnInRange(header, "Structure Level")

    EnsureFolder outDir

    ' Dictionary für Parent + Structure Level Kombinationen
    Dim dict As Object: Set dict = CreateObject("Scripting.Dictionary")
    Dim r As Range, pv As String, slv As String, combinedKey As String
    For Each r In data.rows
        pv = Trim(CStr(r.Cells(1, colParent).Value))
        
        ' NEUE REGEL: Zeilen ohne Parent überspringen (nicht exportieren)
        If pv = "" Then
            ' Überspringe diese Zeile komplett - wird nicht exportiert
            GoTo NextRow
        End If
        
        ' Structure Level hinzufügen (falls Spalte existiert)
        If colStructureLevel > 0 Then
            slv = Trim(CStr(r.Cells(1, colStructureLevel).Value))
            If slv = "" Then slv = "0"
            
            ' NEUE REGEL: Structure Level 0 auch überspringen
            If slv = "0" Then
                GoTo NextRow
            End If
            
            combinedKey = pv & "|LEVEL" & slv
        Else
            combinedKey = pv & "|LEVEL0"
        End If
        
        If Not dict.Exists(combinedKey) Then dict.Add combinedKey, 1
        
NextRow:
    Next r

    Dim k As Variant
    For Each k In dict.Keys
        ' Key aufteilen: Parent|LEVELx
        Dim keyParts As Variant: keyParts = Split(CStr(k), "|")
        Dim parentPart As String: parentPart = keyParts(0)
        Dim levelPart As String: levelPart = keyParts(1)  ' z.B. "LEVEL2"
        
        Dim tmp As Workbook, wsTmp As Worksheet
        Set tmp = Workbooks.Add(xlWBATWorksheet)
        Set wsTmp = tmp.Worksheets(1)

        ' WICHTIG: Header auch als Text formatieren
        Dim headerRange As Range
        Set headerRange = wsTmp.Range("A1").Resize(1, header.Columns.Count)
        headerRange.NumberFormat = "@"
        headerRange.Value = header.Value
        
        ' ===== SAP-KONFORME SPALTENNAMEN =====
        ' SAP-System erwartet spezifische technische Feldnamen
        ' Excel-freundliche Namen -> SAP-technische Namen
        ' Beispiel: "Raw Material Amount" -> "ROMEN_BI" (SAP Rohstoffmenge)
        Dim headerCell As Range
        For Each headerCell In headerRange.Cells
            Select Case Trim(CStr(headerCell.Value))
                Case "Raw Material Amount": headerCell.Value = "ROMEN_BI"      ' Rohstoffmenge
                Case "Raw Material Quantity": headerCell.Value = "ROANZ_BI"    ' Rohstoffanzahl
                Case "Raw Dimension 1": headerCell.Value = "ROMS1_BI"          ' Rohstoff-Maß 1
                Case "Raw Dimension 2": headerCell.Value = "ROMS2_BI"          ' Rohstoff-Maß 2
                Case "Raw Dimension 3": headerCell.Value = "ROMS3_BI"          ' Rohstoff-Maß 3
                Case "Raw Dimension Unit": headerCell.Value = "ROMEI"          ' Rohstoff-Maßeinheit
                Case "Formular Key": headerCell.Value = "RFORM"                ' Formular-Schlüssel
                Case "Raw Material Amount Unit": headerCell.Value = "ROKME"    ' Rohstoffmenge Einheit
            End Select
        Next headerCell

        Dim writeRow As Long: writeRow = 2
        For Each r In data.rows
            Dim rParent As String: rParent = Trim(CStr(r.Cells(1, colParent).Value))
            
            ' NEUE REGEL: Zeilen ohne Parent überspringen (nicht exportieren)
            If rParent = "" Then
                GoTo NextExportRow
            End If
            
            Dim rLevel As String
            If colStructureLevel > 0 Then
                rLevel = Trim(CStr(r.Cells(1, colStructureLevel).Value))
                If rLevel = "" Then rLevel = "0"
                
                ' NEUE REGEL: Structure Level 0 auch überspringen
                If rLevel = "0" Then
                    GoTo NextExportRow
                End If
                
                rLevel = "LEVEL" & rLevel
            Else
                rLevel = "LEVEL0"
            End If
            
            ' Nur Zeilen mit passender Parent + Level Kombination
            If rParent = parentPart And rLevel = levelPart Then
                ' WICHTIG: Text-Format für alle Zellen setzen BEVOR Werte kopiert werden
                Dim targetRange As Range
                Set targetRange = wsTmp.Range("A" & writeRow).Resize(1, header.Columns.Count)
                targetRange.NumberFormat = "@"
                
                ' Werte als String kopieren um "000" -> "0" zu vermeiden
                Dim colIdx As Long
                For colIdx = 1 To header.Columns.Count
                    targetRange.Cells(1, colIdx).Value = CStr(r.Cells(1, colIdx).Value)
                Next colIdx
                
                writeRow = writeRow + 1
            End If
            
NextExportRow:
        Next r

        ' ===== EINHEITEN IN GROSSBUCHSTABEN =====
        ' SAP-Anforderung: Alle Einheiten-Werte müssen UPPERCASE sein
        ' Beispiel: "ea" -> "EA", "st" -> "ST", "mm" -> "MM"
        ' Betrifft nur Einheiten-Spalten (nicht Beschreibungen, DocPart etc.)
        Dim unitColumns As Variant
        unitColumns = Array("MEINS", "ROMEI", "ROMEN_BI", "ROANZ_BI", "ROMS1_BI", "ROMS2_BI", "ROMS3_BI", "RFORM", "ROKME")
        Dim unitCol As Variant, tmpCol As Long, tmpRow As Long
        For Each unitCol In unitColumns
            tmpCol = FindHeaderColumnInRange(wsTmp.rows(1), CStr(unitCol))
            If tmpCol > 0 Then
                ' Alle Werte in dieser Spalte in Großbuchstaben konvertieren (außer Header)
                For tmpRow = 2 To writeRow - 1
                    wsTmp.Cells(tmpRow, tmpCol).Value = UCase(CStr(wsTmp.Cells(tmpRow, tmpCol).Value))
                Next tmpRow
            End If
        Next unitCol
        
        ' Parent und Structure Level Spalten aus Export entfernen
        Dim tmpParentCol As Long
        tmpParentCol = FindHeaderColumnInRange(wsTmp.rows(1), "Parent")
        If tmpParentCol > 0 Then wsTmp.Columns(tmpParentCol).Delete
        
        Dim tmpStructureCol As Long
        tmpStructureCol = FindHeaderColumnInRange(wsTmp.rows(1), "Structure Level")
        If tmpStructureCol > 0 Then wsTmp.Columns(tmpStructureCol).Delete

        ' Dateiname: Parent_LEVELx
        Dim baseName As String
        baseName = StripS4Prefix(parentPart)        ' S+4 abschneiden
        
        Dim safeName As String
        safeName = SanitizeFileName(baseName)
        If Len(safeName) = 0 Then safeName = "UNKNOWN_PARENT"
        
        ' Structure Level am Ende anhängen
        Dim fileName As String
        fileName = safeName & "_" & levelPart & ".csv"

        tmp.SaveAs Filename:=outDir & "\" & fileName, FileFormat:=xlCSVUTF8, Local:=True
        
        tmp.Close SaveChanges:=False
    Next k

    MsgBox "CSV export completed to: " & outDir, vbInformation
End Sub

' ===== FINDET SPALTEN-INDEX ANHAND HEADER-NAME =====
' Verwendet in: ExportCsvByParent_FromNamed (Parent/Structure Level finden)
' Sucht case-insensitive im Header nach Spaltenname
' 
' WICHTIG: Return ist RELATIVER Index (1-basiert)
'   - Nicht absoluter Excel-Spalten-Index!
'   - headerRow.Column wird abgezogen
'   - Beispiel: Header in Spalte D, Gesuchte Spalte E -> Return 2 (nicht 5!)
' 
' Return: 0 wenn nicht gefunden, sonst relative Position (1, 2, 3, ...)
Private Function FindHeaderColumnInRange(headerRow As Range, headerText As String) As Long
    Dim c As Range
    For Each c In headerRow.Cells
        ' Case-insensitive Vergleich (LCase = lowercase)
        If LCase$(Trim$(CStr(c.Value))) = LCase$(headerText) Then
            ' Berechne relative Position: (Absolute Spalte) - (Header-Start) + 1
            FindHeaderColumnInRange = c.Column - headerRow.Column + 1
            Exit Function
        End If
    Next c
    FindHeaderColumnInRange = 0  ' Nicht gefunden
End Function

' ===== ERSTELLT ORDNER FALLS NICHT VORHANDEN =====
' Verwendet in: ExportCsvByParent_FromNamed (C:\TEMP\ sicherstellen)
' Verwendet FileSystemObject (FSO) statt VBA MkDir (robuster)
' WICHTIG: Erstellt nur EINEN Ordner-Level, NICHT rekursiv!
'   - "C:\TEMP" funktioniert (wenn C:\ existiert)
'   - "C:\TEMP\Sub\Deep" schlägt fehl wenn "Sub" nicht existiert
Private Sub EnsureFolder(ByVal pathStr As String)
    Dim fso As Object: Set fso = CreateObject("Scripting.FileSystemObject")  ' Late Binding
    If Not fso.FolderExists(pathStr) Then fso.CreateFolder pathStr  ' Erstelle nur wenn nicht vorhanden
End Sub

' ===== BEREINIGT STRINGS FÜR WINDOWS-DATEINAMEN =====
' Verwendet in: ExportCsvByParent_FromNamed (Parent-Namen für CSV-Dateien)
' Entfernt/ersetzt ungültige Windows-Dateinamen-Zeichen
' 
' Ungültige Zeichen: \ / : * ? " < > |
' Ersetzt durch: _ (Unterstrich)
' Max. Länge: 200 Zeichen (Windows-Limit ist 255, aber Sicherheitspuffer)
' 
' Beispiele: "ABC/DEF" -> "ABC_DEF", "File*.txt" -> "File_.txt"
Private Function SanitizeFileName(ByVal s As String) As String
    Dim badChars As Variant, ch As Variant
    ' Array mit allen ungültigen Windows-Dateinamen-Zeichen
    badChars = Array("\\", "/", ":", "*", "?", """", "<", ">", "|")
    
    Dim res As String: res = Trim(s)  ' Trimme Whitespace zuerst
    
    ' Ersetze jedes ungültige Zeichen durch Unterstrich
    For Each ch In badChars
        res = Replace(res, ch, "_")
    Next ch
    
    ' Kürze auf max. 200 Zeichen (Sicherheit für lange Pfade)
    If Len(res) > 200 Then res = Left(res, 200)
    
    SanitizeFileName = res
End Function

' ===== ERMITTELT DOWNLOADS-ORDNER DES USERS =====
' Verwendet in: ImportSourceFromXlsx (FileDialog Startpfad)
' Standardpfad: C:\Users\<Username>\Downloads
' Fallback: C:\Users\<Username> (falls Downloads nicht existiert)
' 
' Verwendet Environ$("USERPROFILE") statt hartkodiertem Pfad
'   - Funktioniert auf allen Windows-Systemen
'   - Unabhängig von Username oder Laufwerksbuchstabe
Private Function GetDownloadsPath() As String
    Dim p As String
    ' Baue Downloads-Pfad: %USERPROFILE%\Downloads
    ' Beispiel: C:\Users\Max\Downloads
    p = Environ$("USERPROFILE") & "\\Downloads"
    
    ' Prüfe ob Ordner existiert (Dir$ gibt leeren String wenn nicht vorhanden)
    If Len(Dir$(p, vbDirectory)) > 0 Then
        GetDownloadsPath = p  ' Downloads-Ordner existiert
    Else
        ' Fallback: Benutzerprofil-Ordner (sollte immer existieren)
        GetDownloadsPath = Environ$("USERPROFILE")  ' C:\Users\Max
    End If
End Function

' ============ XLSX importieren: 1. Sheet, CurrentRegion ab A1 -> "source" ============
Public Sub ImportSourceFromXlsx(Optional ByVal showMsg As Boolean = True)
    ' Berechnungsmodus merken + PAUSIEREN
    ' Sonst starten PartA/B/C Python-Neuberechnung wenn Clear_DataSheets
    ' die Named Ranges löscht.
    Dim prevCalc As XlCalculation
    prevCalc = Application.Calculation
    Application.Calculation = xlCalculationManual
    
    On Error GoTo CleanFail

    If gPickerActive Then Exit Sub      ' bereits offen ? nochmaligen Dialog verhindern
    If gBusy > 0 Then Exit Sub          ' falls gerade „busy“, nicht reinlaufen

    gPickerActive = True                ' Guard setzen
    Dim prevScr As Boolean, prevEvt As Boolean, prevInt As Boolean
    prevScr = Application.ScreenUpdating
    prevEvt = Application.EnableEvents
    prevInt = Application.Interactive

    ' UI sicher aktiv
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    Application.Interactive = True

    ' Besser als GetOpenFilename: stabiler und weniger „Doppel-Open“-Glitches
    Dim fd As FileDialog, chosen As String
    Set fd = Application.FileDialog(msoFileDialogFilePicker)
    With fd
        .Title = "Please select XLSX file with source data"
        .AllowMultiSelect = False
        .Filters.Clear
        .Filters.Add "Excel Workbook (*.xlsx)", "*.xlsx"
        .InitialFileName = GetDownloadsPath & Application.PathSeparator
        If .Show <> -1 Then
            If showMsg Then MsgBox "No file selected. Import cancelled.", vbInformation
            ' Bei Abbruch: Daten löschen (noch im Manual-Modus, Python triggert nicht)
            Clear_DataSheets
            ' Berechnungsmodus WIEDERHERSTELLEN damit Excel normal weiterarbeitet.
            ' Python-Zellen rechnen kurz mit fehlenden Inputs und bekommen Error-DataFrame,
            ' aber Load_ExcelButton wartet nicht darauf (checkRegion = Nothing).
            Application.Calculation = prevCalc
            GoTo CleanUp
        End If
        chosen = .SelectedItems(1)
    End With
    
    ' WICHTIG: Excel-Fenster im Vordergrund behalten nach Dialog
    On Error Resume Next
    AppActivate Application.Caption
    ThisWorkbook.Windows(1).Activate
    On Error GoTo 0

    ' Ab hier: busy
    If Not EnterBusy() Then GoTo CleanUp
    
    Application.ScreenUpdating = False
    
    ' Alte Daten löschen JETZT (nachdem User eine Datei gewählt hat)
    ' Calculation ist Manual -> Python triggert NICHT (gewollt).
    ' Erst Load_ExcelButton setzt auf Automatic NACH dem Import.
    Clear_DataSheets
    
    Dim wbThis As Workbook
    Set wbThis = ThisWorkbook

    Dim wbSrc As Workbook, wsSrc As Worksheet, rng As Range
    Set wbSrc = Workbooks.Open(chosen, ReadOnly:=True, UpdateLinks:=False, Notify:=False)
    Set wsSrc = wbSrc.Worksheets(1)
    
    ' Sofort wieder zu ThisWorkbook zurückkehren
    wbThis.Activate

    ' ===== CURRENTREGION: Automatische Datenbereich-Erkennung =====
    ' CurrentRegion ab A1 -> Erkennt automatisch zusammenhängenden Datenbereich
    ' Sucht ab A1 in alle Richtungen bis zur ersten komplett leeren Zeile/Spalte
    ' Beispiel: Daten von A1 bis AD3000 -> CurrentRegion = A1:AD3000
    ' Vorteil: Funktioniert unabhängig von tatsächlicher Datengröße
    On Error Resume Next
    Set rng = wsSrc.Range("A1").CurrentRegion  ' Hole zusammenhängenden Bereich ab A1
    On Error GoTo 0
    If rng Is Nothing Then Err.Raise vbObjectError + 4131, , "Could not detect CurrentRegion from A1."

    Dim rCount As Long, cCount As Long
    Dim colPTp As Long, colQty As Long, colQtyUnit As Long
    rCount = rng.rows.Count
    cCount = rng.Columns.Count

    Dim wsDst As Worksheet
    Set wsDst = EnsureSheet("source")
    wsDst.Cells.Clear
    
    ' ===== KRITISCHER SCHRITT: Text-Formatierung VOR Wertzuweisung =====
    ' Problem: Excel konvertiert automatisch Strings zu Zahlen
    '   - "000" wird zu "0"
    '   - "920" wird zu 920.0
    '   - Führende Nullen gehen verloren
    ' Lösung: ERST NumberFormat = "@" (Text), DANN Wert als String setzen
    ' @ = Excel's internes Text-Format Symbol
    ' 
    ' Wichtig: Reihenfolge ist entscheidend!
    '   1. NumberFormat = "@" (Zelle als Text markieren)
    '   2. Value = CStr(...) (Wert als String zuweisen)
    Dim i As Long, j As Long
    For i = 1 To rCount
        ' StatusBar-Feedback alle 100 Zeilen (damit User sieht dass es läuft)
        If i Mod 100 = 0 Or i = 1 Or i = rCount Then
            SafeStatusBar "Import: Processing row " & i & " / " & rCount & "..."
            DoEvents
        End If
        For j = 1 To cCount
            Dim cellValue As Variant
            cellValue = rng.Cells(i, j).Value
            
            ' SCHRITT 1: Formatiere Zielzelle als Text VOR dem Setzen des Wertes
            wsDst.Cells(i, j).NumberFormat = "@"  ' @ = Text-Format
            
            ' SCHRITT 2: Setze Wert als String um Formatierung zu erhalten
            If Not IsEmpty(cellValue) Then
                wsDst.Cells(i, j).Value = CStr(cellValue)  ' Explizite String-Konvertierung
            Else
                wsDst.Cells(i, j).Value = ""
            End If
        Next j
    Next i

    SafeStatusBar "Import: Closing source file..."
    wbSrc.Close SaveChanges:=False
    SafeStatusBar False

    Dim tgt As Range
    Set tgt = wsDst.Range("A1").Resize(rCount, cCount)
    SetNamedRange "SourceRegion", tgt

    ' ===== PTp-LOGIK: Automatisches Setzen von Quantity/Unit für PTp="D" =====
    ' PTp = Part Type (L=Line, R=Reference, D=Document)
    ' Geschäftsregel: Dokumente (PTp="D") haben immer Menge=1 und Einheit="ea"
    ' Diese Logik wird INLINE beim Import angewendet (keine separate Funktion)
    ' Später in PartC wird "ea" zu "ST" konvertiert (SAP-konforme Einheit)
    
    ' Schritt 1: Finde relevante Spalten im Header (Zeile 1)
    For j = 1 To cCount
        Select Case Trim$(LCase(wsDst.Cells(1, j).Value))
            Case "ptp": colPTp = j              ' Part Type Spalte
            Case "quantity": colQty = j          ' Menge Spalte
            Case "quantity unit": colQtyUnit = j ' Einheit Spalte
        End Select
    Next j

    ' Schritt 2: Nur wenn alle drei Spalten gefunden wurden
    If colPTp > 0 And colQty > 0 And colQtyUnit > 0 Then
        ' Durchlaufe alle Datenzeilen (ab Zeile 2, da Zeile 1 = Header)
        For i = 2 To rCount
            ' Wenn PTp = "D" (case-insensitive) -> überschreibe Quantity und Unit
            If UCase$(Trim$(wsDst.Cells(i, colPTp).Value)) = "D" Then
                wsDst.Cells(i, colQty).Value = "1"     ' Menge immer 1 für Dokumente
                wsDst.Cells(i, colQtyUnit).Value = "ea" ' Einheit "ea" (später -> "ST")
            End If
        Next i
    End If
    
    ' ===== DOCTYPE BEREINIGUNG: Auf 3 Zeichen kürzen =====
    ' Entfernt Suffix wie "DOK - xyz" -> "DOK"
    Dim colDocType As Long: colDocType = 0
    For j = 1 To cCount
        If Trim$(LCase(wsDst.Cells(1, j).Value)) = "doctype" Then
            colDocType = j
            Exit For
        End If
    Next j
    
    If colDocType > 0 Then
        For i = 2 To rCount
            Dim docTypeVal As String
            docTypeVal = Trim$(wsDst.Cells(i, colDocType).Value)
            If Len(docTypeVal) > 3 Then
                wsDst.Cells(i, colDocType).Value = Left$(docTypeVal, 3)
            End If
        Next i
    End If
    
    ' ===== QEP/DRW FILTER: Entferne Zeilen mit DocType QEP oder DRW =====
    ' Nur wenn Config-Option aktiviert ist
    InitializeConfigSheet
    Dim filterQepDrw As String
    filterQepDrw = UCase(Trim(GetConfigValue("FilterQepDrwDocTypes")))
    
    If filterQepDrw = "YES" And colDocType > 0 Then
        ' Von unten nach oben durchgehen um Zeilen sicher zu löschen
        For i = rCount To 2 Step -1
            Dim docType As String
            docType = UCase$(Trim$(wsDst.Cells(i, colDocType).Value))
            If docType = "QEP" Or docType = "DRW" Then
                wsDst.Rows(i).Delete
            End If
        Next i
    End If

    If showMsg Then MsgBox "Import successful from: " & chosen, vbInformation
    
    ' Button-Aktivierung wird vom Aufrufer (Load_ExcelButton) gemacht
    ' damit sie erst NACH UpdateSourceRegion (8 Sek Wartezeit) erscheinen

CleanUp:
    Application.ScreenUpdating = prevScr
    Application.EnableEvents = prevEvt
    Application.Interactive = prevInt
    If gBusy > 0 Then ExitBusy
    gPickerActive = False
    Exit Sub

CleanFail:
    MsgBox "Error during import: " & Err.Description, vbCritical
    Clear_DataSheets
    EnableAllButtons
    ' Berechnungsmodus WIEDERHERSTELLEN damit Excel nicht auf Manual hängen bleibt
    Application.Calculation = prevCalc
    Resume CleanUp
End Sub