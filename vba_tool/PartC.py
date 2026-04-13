# ===== PartC (liest ToDoRegion, transformiert, gibt DataFrame zurück => Spill) =====
import pandas as pd, re, numpy as np

def normalize_str(x):
    if pd.isna(x): return ''
    return str(x).strip()

def is_filled(x):
    return normalize_str(x) != ''

def to_scalar(v):
    # IMMER als String zurückgeben um "000" -> "0" Konvertierung zu vermeiden
    if pd.isna(v):
        return ''
    # String-Konvertierung um Format zu erhalten (wichtig für DocPart, DocVersion etc.)
    result = str(v)
    if result.lower() in ['nan', 'none', 'nat', '<na>']:
        return ''
    return result

# --- Standard-Ausgabe initialisieren ---
out_df = pd.DataFrame({"PYERROR": ["Unknown error"]})

# --- 0) Quelle laden ---
try:
    df = xl("ToDoRegion", headers=True).copy()
    if df is None or len(df) == 0:
        out_df = pd.DataFrame({"PYERROR": ["ToDoRegion is empty"]})
    else:
        # SOFORT alle Spalten zu String konvertieren um Formatverluste zu vermeiden
        for col in df.columns:
            df[col] = df[col].astype(str).replace({'nan': '', 'None': '', '<NA>': '', 'nat': ''})
            # Spezielle Behandlung für numeric-ähnliche Strings
            df[col] = df[col].apply(lambda x: '' if str(x).lower() in ['nan', 'none', 'nat'] else str(x))
        
except Exception as e:
    out_df = pd.DataFrame({"PYERROR": [f"ToDoRegion missing/invalid: {e}"]})
else:
    # --- 1) Spalten sicherstellen ---
    needed = [
        'Pos','DocType','DocPart','Version','Made From','Mat/Doc Number',
        'Quantity Unit','Reference Designator','ERP Position Text','Structure Level','LvL',
        'State','Subtyp','SAP Downstream','Assembly','Parent','PosText',
        'MatScr','MatDest','Plant','DisconType','DisconDate','DisconGrp','SuccessGrp',
        'Description','Quantity','Raw Dimension 1','Raw Dimension 2','Raw Dimension 3',
        'Raw Dimension Unit','Raw Material Amount','Raw Material Amount Unit',
        'Raw Material Quantity','Formular Key','PTp'
    ]
    for c in needed:
        if c not in df.columns:
            df[c] = ''  # Leere Strings statt pd.NA

    # Wichtige Spalten als String forcieren um "000" -> "0" zu vermeiden
    # BEREITS ALLE SPALTEN ALS STRINGS - nur zur Sicherheit nochmals kritische Spalten
    string_cols = ['DocPart', 'DocType', 'Version', 'Mat/Doc Number', 'Description', 'Pos']
    for col in string_cols:
        if col in df.columns:
            # Zusätzliche String-Sicherung für kritische Spalten
            df[col] = df[col].astype(str)

    # --- 2) nur Zeilen mit Pos ---
    df = df[df['Pos'].apply(is_filled)].reset_index(drop=True)

    # --- 3) [12345-1] im RD entfernen ---
    def remove_bracketed_numbers(s):
        if pd.isna(s): return s
        return re.sub(r"\[\d+-\d+\]", "", str(s))
    if 'Reference Designator' in df.columns:
        df['Reference Designator'] = df['Reference Designator'].apply(remove_bracketed_numbers)

    # --- 4) DocType leer -> DocPart/Version leeren ---
    mask_doctype_empty = ~df['DocType'].apply(is_filled)
    df.loc[mask_doctype_empty, ['DocPart','Version']] = ''

    # --- 5) Made From nach Mat/Doc Number ---
    mask_made_from = df['Made From'].apply(is_filled)
    if mask_made_from.any():
        df.loc[mask_made_from, 'Mat/Doc Number'] = df.loc[mask_made_from, 'Made From'].astype(str)

    # --- 6) Einheit: ea -> ST ---
    for col in ['Quantity Unit', 'Raw Material Amount Unit', 'Raw Material Quantity Unit']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: 'ST' if normalize_str(x).lower() == 'ea' else x)

    # --- 7) Quellfelder entfernen (OHNE Structure Level) ---
    cols_to_drop = [
        'LvL','State','Subtyp','SAP Downstream','Assembly',
        'Made From','Reference Designator','ERP Position Text'
    ]
    existing_drops = [c for c in cols_to_drop if c in df.columns]
    if existing_drops:
        df.drop(columns=existing_drops, inplace=True, errors='ignore')

    # --- 8) Umbenennen & Zielschema ---
    df = df.rename(columns={'Version': 'DocVersion', 'Quantity Unit': 'MEINS'})
    target_cols = [
        'MatScr','MatDest','Plant','DisconType','DisconDate','DisconGrp','SuccessGrp',
        'Pos','PTp','Mat/Doc Number','DocType','DocPart','DocVersion','Description',
        'Quantity','MEINS','PosText','Raw Material Amount','Raw Material Quantity',
        'Raw Dimension 1','Raw Dimension 2','Raw Dimension 3','Raw Dimension Unit',
        'Formular Key','Raw Material Amount Unit'
    ]
    
    # Fehlende Spalten hinzufügen
    missing_cols = [c for c in target_cols if c not in df.columns]
    for c in missing_cols:
        df[c] = ''

    # Parent-Spalte UND Structure Level separat behandeln
    include_parent = 'Parent' in df.columns
    include_structure_level = 'Structure Level' in df.columns
    final_cols = target_cols + (['Parent'] if include_parent else []) + (['Structure Level'] if include_structure_level else [])
    out_df = df[final_cols].copy()

    # --- 9) Spill robust machen ---
    out_df = out_df.reset_index(drop=True)
    out_df.columns = [str(c) for c in out_df.columns]

    # Optimierte String-Formatierung - nur problematische Werte ersetzen
    try:
        # Schnellere Methode: fillna zuerst, dann String-Konvertierung
        out_df = out_df.fillna('')
        
        # Nur bei kritischen Spalten String-Konvertierung erzwingen
        critical_cols = ['DocPart', 'DocType', 'DocVersion', 'Mat/Doc Number', 'Pos']
        for col in critical_cols:
            if col in out_df.columns:
                out_df[col] = out_df[col].astype(str)
        
        # Finale Bereinigung - nur einmal und optimiert
        out_df = out_df.replace(['nan', 'None', '<NA>', 'nat'], '')
        
    except Exception:
        # Fallback: einfache Bereinigung
        out_df = out_df.fillna('')

# --- 10) LETZTE ZEILE: garantiert ein DataFrame -> Spill ---
out_df