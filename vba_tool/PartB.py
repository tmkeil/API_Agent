# ----- PartB (liest ToDoRegion, gibt IMMER einen String zurück) -----
import pandas as pd

def normalize_str(x):
    if pd.isna(x): return ''
    return str(x).strip()

def is_filled(x):
    return normalize_str(x) != ''

def try_load_todo():
    """Sichere ToDoRegion-Ladung mit umfassender Fehlerbehandlung"""
    try:
        # Prüfe zuerst, ob Region überhaupt existiert
        df = xl("ToDoRegion", headers=True)
        
        # Validiere DataFrame
        if not isinstance(df, pd.DataFrame):
            return None
            
        if df is None or len(df) == 0:
            return None
            
        # Prüfe auf Error-Inhalte
        if len(df.columns) == 1 and any('ERROR' in str(col).upper() or 'FEHLER' in str(col).upper() for col in df.columns):
            return None
            
        return df.copy()
        
    except Exception as e:
        # Alle Excel-Fehler, einschließlich 2051, abfangen
        return None

# --- immer einen Output-String setzen
__out = "PYERROR: Unknown state."

df2 = try_load_todo()
if df2 is None:
    __out = "ERROR: ToDoRegion not available or empty. Please run PartA first (Button A - Create ToDo table)."
else:
    needed_cols = [
        'Made From','Raw Dimension 1','Raw Dimension 2','Raw Dimension 3','Raw Dimension Unit',
        'Pos','State','Subtyp','PTp','DocPart','DocType','Version','Structure Level'
    ]
    for c in needed_cols:
        if c not in df2.columns:
            df2[c] = ''  # Leere Strings statt pd.NA

    # NUR Zeilen mit Structure Level >= 1 validieren
    if 'Structure Level' in df2.columns:
        # Filtere auf Structure Level >= 1 für Validierung
        mask_level_1_plus = df2['Structure Level'].astype(str).apply(
            lambda x: x.strip() != '' and x.strip() != '0'
        )
        df_to_validate = df2[mask_level_1_plus].copy()
    else:
        df_to_validate = df2.copy()

    validation_issues = []
    raw_fields = ['Raw Dimension 1','Raw Dimension 2','Raw Dimension 3','Raw Dimension Unit']

    # [Regel] Made From -> mind. eines der RAW-Felder muss befüllt sein
    need_raw_mask = df_to_validate['Made From'].apply(is_filled)
    no_raw_filled_mask = need_raw_mask & ~(df_to_validate[raw_fields].applymap(is_filled).any(axis=1))
    for idx in df_to_validate[no_raw_filled_mask].index:
        # Zeige die ORIGINALE Zeilennummer (vor Filterung)
        original_row = df2.index.get_loc(idx) + 2
        validation_issues.append(f"Row {original_row}: 'Made From' is set, but no RAW-Dimension field/unit is filled.")

    # [Regel] Bei gesetzter Pos muss State RELEASED oder PUBLISHED sein (case-insensitive)
    ok_states = {'RELEASED', 'PUBLISHED'}
    state_norm = df_to_validate['State'].astype(str).str.strip().str.upper()
    bad_state_mask = df_to_validate['Pos'].apply(is_filled) & ~state_norm.isin(ok_states)
    for idx in df_to_validate[bad_state_mask].index:
        original_row = df2.index.get_loc(idx) + 2
        validation_issues.append(f"Row {original_row}: Pos set but State='{df_to_validate.at[idx,'State']}' (not RELEASED/PUBLISHED).")

    # [Regel] Kein "Collection" (egal welche Variante) mit gesetzter Pos
    coll_mask = df_to_validate['Pos'].apply(is_filled) & df_to_validate['Subtyp'].astype(str).str.strip().str.casefold().str.contains('collection')
    for idx in df_to_validate[coll_mask].index:
        original_row = df2.index.get_loc(idx) + 2
        validation_issues.append(f"Row {original_row}: 'Collection' entry with set Pos is not allowed.")

    # [Regel] PTp = D -> DocPart/DocType/Version müssen vollständig sein
    mask_ptp_d = df_to_validate['PTp'].astype(str).str.strip().str.upper() == 'D'
    missing_doc_fields_mask = mask_ptp_d & ~(
        df_to_validate[['DocPart','DocType','Version']].applymap(is_filled).all(axis=1)
    )
    for idx in df_to_validate[missing_doc_fields_mask].index:
        original_row = df2.index.get_loc(idx) + 2
        validation_issues.append(f"Row {original_row}: PTp='D' but DocPart/DocType/Version incomplete.")

    # >>> [Regel] PTp = L oder R -> Quantity und Quantity Unit müssen befüllt sein
    ptp_norm = df_to_validate['PTp'].astype(str).str.strip().str.upper()
    mask_ptp_lr = ptp_norm.isin(['L','R'])
    missing_qty_mask = mask_ptp_lr & ~(
        df_to_validate[['Quantity','Quantity Unit']].applymap(is_filled).all(axis=1)
    )
    for idx in df_to_validate[missing_qty_mask].index:
        original_row = df2.index.get_loc(idx) + 2
        validation_issues.append(
            f"Row {original_row}: PTp='{df_to_validate.at[idx,'PTp']}' but 'Quantity' and/or 'Quantity Unit' missing."
        )
        
    # Ausgabe (ohne doppelte Runde)
    summary = "\n".join(f"• {m}" for m in validation_issues)
    __out = summary if summary else "No validation errors found."

# LETZTE ZEILE: immer ein String -> Excel-Wert zeigt Text, VBA liest Text
__out