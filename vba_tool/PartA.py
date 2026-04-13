import re, pandas as pd
from collections import OrderedDict

def norm(x):
    if x is None or (isinstance(x, float) and pd.isna(x)): return ''
    s = str(x).strip()
    return '' if s.lower() in ['#nv','none','nan'] else s

def filled(x): return norm(x) != ''

def exp_tok(t):
    t = t.strip()
    if not t: return []
    m = re.fullmatch(r"([A-Za-z]+)\s*(\d+)\s*-\s*([A-Za-z]+)\s*(\d+)", t)
    if m:
        p1,s,p2,e = m.groups()
        if p1.upper() != p2.upper(): return [t]
        s,e = int(s),int(e)
        r = range(s,e+1) if s<=e else range(s,e-1,-1)
        return [f"{p1.upper()}{i}" for i in r]
    m2 = re.fullmatch(r"([A-Za-z]+)\s*(\d+)", t)
    if m2:
        p,n = m2.groups()
        return [f"{p.upper()}{int(n)}"]
    return [t]

def exp_rd(s):
    if not filled(s): return ''
    s2 = s.replace(';',',')
    pts = [p.strip() for p in s2.split(',') if p.strip()]
    ex = []
    for tok in pts: ex.extend(exp_tok(tok))
    nd = [norm(x).replace(' ','') for x in ex if norm(x)]
    dd = list(OrderedDict.fromkeys(nd))
    return ",".join(dd)

_BNR = re.compile(r"\[\s*\d+\s*-\s*\d+\s*\]")
def strip_br(t):
    if not filled(t): return ''
    s = _BNR.sub("", str(t))
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s*,\s*", ",", s)
    return s.strip(", ")

sc = ['Structure Level','LvL','Pos','PTp','Mat/Doc Number','State','Subtyp','SAP Downstream','Assembly','Parent','Made From','MatScr','MatDest','Plant','DisconType','DisconDate','DisconGrp','SuccessGrp','Description','DocPart','DocType','Version','Quantity','Quantity Unit','Reference Designator','ERP Position Text','Raw Dimension 1','Raw Dimension 2','Raw Dimension 3','Raw Dimension Unit','Raw Material Amount','Raw Material Amount Unit','Raw Material Quantity','Raw Material Quantity Unit','Formular Key','Printing Good']

try:
    src_data = xl("SourceRegion", headers=True)
    if isinstance(src_data, str):
        raise ValueError(f"SourceRegion returned error: {src_data}")
    df = src_data.copy()
    df = df.fillna('').replace(['nan','None','<NA>','nat','NaN'],'')
    for c in ['DocPart','DocType','Version','Mat/Doc Number']:
        if c in df.columns: df[c] = df[c].astype(str)
    ec = [c for c in sc if c in df.columns]
    df = df[ec]
    for c in sc:
        if c not in df.columns: df[c] = ''
except Exception as e:
    df = pd.DataFrame({"ERROR": [f"Data loading error: {str(e)}"]})
    ec = ["ERROR"]

try:
    if 'Mat/Doc Number' in df.columns and len(df)>0:
        df['Mat/Doc Number'] = df['Mat/Doc Number'].astype(str).str.replace('^7000','',regex=True).str.replace(r'^S[A-Za-z0-9]{4}','',regex=True).str.strip()
except: pass

try:
    if 'Structure Level' in df.columns and 'Parent' in df.columns and len(df)>0:
        df.loc[df['Structure Level'].astype(str)=='0','Parent'] = ''
except: pass

try:
    cfg_apply = 'YES'
    try:
        cfg_sheet = xl("_Config!F1:F1", headers=False)
        if cfg_sheet is not None and len(cfg_sheet)>0:
            cfg_apply = str(cfg_sheet.iloc[0,0]).strip().upper()
    except: pass
    
    if cfg_apply == 'YES' and all(c in df.columns for c in ['Subtyp','Printing Good','Parent','Structure Level']) and len(df)>0:
        # Printing Good Werte normalisieren: True/False/Yes/No/1/0 → YES/NO (case insensitive)
        pg_map = {'yes':'YES','no':'NO','true':'YES','false':'NO','1':'YES','0':'NO','ja':'YES','nein':'NO'}
        df['Printing Good'] = df['Printing Good'].apply(lambda x: pg_map.get(norm(x).lower(), norm(x).upper()))
        rd = []
        for i in range(len(df)):
            st = norm(df.at[i,'Subtyp'])
            pg = norm(df.at[i,'Printing Good'])
            if st == 'Enclosed Documentation' and pg == 'NO':
                pv = norm(df.at[i,'Parent'])
                slv = norm(df.at[i,'Structure Level'])
                try: edl = int(slv)
                except: edl = 0
                ff = False
                for ni in range(i+1,len(df)):
                    nst = norm(df.at[ni,'Subtyp'])
                    nsl = norm(df.at[ni,'Structure Level'])
                    try: nl = int(nsl)
                    except: continue
                    if nl <= edl: break
                    if nst == 'Customer related document' and nl > edl:
                        if not ff:
                            df.at[ni,'Parent'] = pv
                            df.at[ni,'Structure Level'] = slv
                            ff = True
                        else:
                            df.at[ni,'Parent'] = pv
                rd.append(i)
        if rd: df = df.drop(index=rd).reset_index(drop=True)
    if 'Printing Good' in df.columns: df = df.drop(columns=['Printing Good'])
except: pass

try:
    if 'PosText' not in df.columns: df['PosText'] = ''
    if len(df)>0 and 'Reference Designator' in df.columns and 'ERP Position Text' in df.columns:
        rc = df['Reference Designator'].astype(str).replace(['nan','None',''],'')
        ec = df['ERP Position Text'].astype(str).replace(['nan','None',''],'')
        df['PosText'] = (rc + ' ' + ec).str.strip()
        if len(df)<=1000:
            df['Reference Designator'] = df['Reference Designator'].apply(exp_rd)
            rc = df['Reference Designator'].astype(str).replace(['nan','None',''],'')
            df['PosText'] = (rc + ' ' + ec).str.strip()
except:
    if 'PosText' not in df.columns: df['PosText'] = ''

try:
    df = df.fillna('').replace(['nan','None','#NV','NaN','<NA>','nat'],'')
    df = df.reset_index(drop=True)
    df.columns = [str(c) for c in df.columns]
    if df is None or len(df)==0: df = pd.DataFrame({"INFO": ["No data processed"]})
except Exception as e:
    df = pd.DataFrame({"ERROR": [f"PartA processing error: {str(e)}"]})

df
