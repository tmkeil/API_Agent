"""
Windchill BOM Export Tool
=========================
Liest die vollständige Stückliste (BOM) eines Produkts aus PTC Windchill aus,
inklusive aller referenzierten Dokumente und CAD-Dokumente.
Ausgabe als hierarchische JSON-Datei.

Verwendung:
    1. Produktnummern zeilenweise in input.txt eintragen
    2. python windchill_bom_export.py
    3. Für jedes Produkt wird eine eigene JSON-Datei erzeugt

Benötigte Pakete:
    pip install requests urllib3
"""

import json
import sys
import os
import datetime
import io
import logging
import threading
import tkinter as tk
from tkinter import messagebox
from collections import OrderedDict
from logging.handlers import RotatingFileHandler

import time

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlparse

from . import wt_bom, wt_documents, wt_parts

# stdout auf UTF-8 umstellen (Windows-Konsole nutzt sonst cp1252)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# SSL-Warnungen für Self-Signed-Zertifikate unterdrücken (Dev-Umgebung)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ─── Konfiguration aus config.json laden ─────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_config_path = os.path.join(PROJECT_ROOT, "config.json")
with open(_config_path, "r", encoding="utf-8") as _f:
    _config = json.load(_f)


WINDCHILL_BASE_URL = _config["windchill_base_url"]
ODATA_VERSION = _config["odata_version"]
INPUT_FILE = _config["input_file"]
OUTPUT_FILE = _config["output_file"]
MAX_BOM_DEPTH = _config.get("max_bom_depth", 50)
HTTP_TIMEOUT = _config.get("http_timeout", 120)
HTTP_RETRIES = _config.get("http_retries", 3)
MAX_PAGES = _config.get("max_pages", 200)
DEBUG = _config.get("debug", True)
READ_WT_DOCUMENTS = _config.get("read_wt_documents", True)
READ_CAD_DOCUMENTS = _config.get("read_cad_documents", True)
SERVER_DISPLAY_NAME = urlparse(WINDCHILL_BASE_URL).netloc or WINDCHILL_BASE_URL


def _init_api_logger() -> logging.Logger:
    """Initialisiert Dateilogger für alle API-Aufrufe."""
    logger = logging.getLogger("wtbomexport.api")
    if logger.handlers:
        return logger

    log_path = os.path.join(PROJECT_ROOT, "wtbomexport.log")
    handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


API_LOGGER = _init_api_logger()


# ─── Fortschritts-Tracker ────────────────────────────────────────────────────
class ProgressTracker:
    """Verfolgt Fortschritt und zeigt eine kompakte Statuszeile an."""

    BAR_WIDTH = 30  # Breite des Fortschrittsbalkens in Zeichen

    def __init__(self):
        self.start_time = time.time()
        self.http_requests = 0
        self.parts_processed = 0
        self.parts_total = 0  # wird gesetzt sobald BOM-Kinder bekannt
        self.docs_found = 0
        self.cad_docs_found = 0
        self.current_part = ""
        self.current_phase = ""
        self._last_status_len = 0

    def set_total_parts(self, total: int):
        self.parts_total = total

    def tick_request(self):
        self.http_requests += 1

    def tick_part(self, part_number: str):
        self.parts_processed += 1
        self.current_part = part_number

    def tick_docs(self, count: int):
        self.docs_found += count

    def tick_cad_docs(self, count: int):
        self.cad_docs_found += count

    def set_phase(self, phase: str):
        self.current_phase = phase

    @property
    def elapsed(self) -> str:
        secs = int(time.time() - self.start_time)
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}h{m:02d}m{s:02d}s"
        elif m:
            return f"{m}m{s:02d}s"
        return f"{s}s"

    def _bar(self) -> str:
        if self.parts_total <= 0:
            return ""
        pct = min(self.parts_processed / self.parts_total, 1.0)
        filled = int(self.BAR_WIDTH * pct)
        bar = "█" * filled + "░" * (self.BAR_WIDTH - filled)
        return f"[{bar}] {pct:.0%}"

    def print_status(self):
        """Kompakte einzeilige Status-Anzeige (überschreibt sich selbst)."""
        bar = self._bar()
        parts_info = (f"{self.parts_processed}/{self.parts_total}"
                      if self.parts_total else f"{self.parts_processed}")
        status = (
            f"\r⏳ {bar}  Parts: {parts_info}  "
            f"Docs: {self.docs_found}  CAD: {self.cad_docs_found}  "
            f"HTTP: {self.http_requests}  ⏱ {self.elapsed}  "
            f"[{self.current_phase}]"
        )
        # Alte Zeichen überschreiben
        padded = status.ljust(self._last_status_len)
        self._last_status_len = len(status)
        print(padded, end="", flush=True)

    def print_final_summary(self):
        """Abschluss-Zusammenfassung nach der Verarbeitung."""
        # Statuszeile abschließen
        print()
        print(f"\n{'─' * 50}")
        print(f"  ⏱  Dauer:            {self.elapsed}")
        print(f"  🌐 HTTP-Requests:    {self.http_requests}")
        print(f"  📦 Parts verarbeitet: {self.parts_processed}")
        print(f"  📄 Dokumente:        {self.docs_found}")
        print(f"  📐 CAD-Dokumente:    {self.cad_docs_found}")
        print(f"{'─' * 50}")


# Globale Instanz (wird pro Produkt-Export zurückgesetzt)
progress = ProgressTracker()


# ─── Login Dialog ────────────────────────────────────────────────────────────
def get_credentials():
    """Zeigt einen Login-Dialog und gibt (username, password) zurück."""
    result = {"username": None, "password": None, "confirmed": False}

    root = tk.Tk()
    root.withdraw()

    dialog = tk.Toplevel(root)
    dialog.title("Windchill Login")
    dialog.geometry("380x210")
    dialog.resizable(False, False)
    dialog.grab_set()
    dialog.focus_force()

    # Fenster zentrieren
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() - 380) // 2
    y = (dialog.winfo_screenheight() - 210) // 2
    dialog.geometry(f"+{x}+{y}")

    # Header
    header_frame = tk.Frame(dialog, bg="#2c3e50", height=50)
    header_frame.pack(fill="x")
    header_frame.pack_propagate(False)
    tk.Label(
        header_frame,
        text="Windchill PLM – BOM Export",
        font=("Segoe UI", 11, "bold"),
        fg="white",
        bg="#2c3e50",
    ).pack(pady=12)

    # Server-Info
    tk.Label(
        dialog,
        text=f"Server: {SERVER_DISPLAY_NAME}",
        font=("Segoe UI", 8),
        fg="#888",
    ).pack(pady=(6, 2))

    # Eingabefelder
    form = tk.Frame(dialog)
    form.pack(pady=6)

    tk.Label(form, text="Benutzer:", font=("Segoe UI", 9)).grid(
        row=0, column=0, sticky="e", padx=(10, 5), pady=3
    )
    user_entry = tk.Entry(form, width=28, font=("Segoe UI", 9))
    user_entry.grid(row=0, column=1, padx=(0, 10), pady=3)
    user_entry.focus_set()

    tk.Label(form, text="Passwort:", font=("Segoe UI", 9)).grid(
        row=1, column=0, sticky="e", padx=(10, 5), pady=3
    )
    pass_entry = tk.Entry(form, width=28, show="●", font=("Segoe UI", 9))
    pass_entry.grid(row=1, column=1, padx=(0, 10), pady=3)

    def on_login(event=None):
        u = user_entry.get().strip()
        p = pass_entry.get()
        if not u or not p:
            messagebox.showwarning(
                "Eingabe fehlt",
                "Bitte Benutzer und Passwort eingeben.",
                parent=dialog,
            )
            return
        result["username"] = u
        result["password"] = p
        result["confirmed"] = True
        dialog.destroy()

    def on_cancel():
        dialog.destroy()

    # Buttons
    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=8)
    tk.Button(
        btn_frame, text="Login", command=on_login, width=12, font=("Segoe UI", 9)
    ).pack(side="left", padx=6)
    tk.Button(
        btn_frame, text="Abbrechen", command=on_cancel, width=12, font=("Segoe UI", 9)
    ).pack(side="left", padx=6)

    # Enter-Taste zum Bestätigen
    dialog.bind("<Return>", on_login)
    dialog.bind("<Escape>", lambda e: on_cancel())
    dialog.protocol("WM_DELETE_WINDOW", on_cancel)

    root.wait_window(dialog)
    root.destroy()

    if not result["confirmed"]:
        return None, None
    return result["username"], result["password"]


# ─── Windchill REST / OData Client ──────────────────────────────────────────
class WindchillClient:
    """Client für die PTC Windchill OData REST API (v6)."""

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.odata_base = f"{self.base_url}/servlet/odata/{ODATA_VERSION}"
        self._request_lock = threading.Lock()
        self.session = requests.Session()
        self.session.verify = False
        self.session.auth = (self.username, self.password)
        self.session.headers.update({
            "Accept": "application/json",
        })

        # Connection-Pool vergrößern (Standard: 10 → 20 parallele Verbindungen)
        adapter = HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=0,  # Retries machen wir selbst in _get()
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self._part_properties = []  # wird bei connect ermittelt
        self._part_cache = {}       # Cache: part_number → part_dict
        self._bom_nav_strategy = None  # gemerktes Navigation-Property für BOM
        self._usage_link_nav = None   # gemerktes Navigation-Property für UsageLink→Child
        self._connect()

    # ── Verbindungsaufbau & API Erkundung ──────────────────────────────────
    def _connect(self):
        """Verbinden, authentifizieren und die API erkunden."""
        print(f"\n  OData Endpoint: {self.odata_base}")

        # ① Erst prüfen ob der Server antwortet
        print("  [1/5] Teste Verbindung...")
        try:
            resp = self._request(
                "GET",
                f"{self.odata_base}/ProdMgmt",
                timeout=30,
                allow_redirects=True,
            )
            if DEBUG:
                print(f"        Status: {resp.status_code}")
                print(f"        Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
                print(f"        URL (nach Redirect): {resp.url}")

            # CSRF-Nonce übernehmen
            nonce = resp.headers.get("CSRF_NONCE")
            if nonce:
                self.session.headers["CSRF_NONCE"] = nonce
                if DEBUG:
                    print(f"        CSRF_NONCE: {nonce[:20]}...")

            if resp.status_code == 401:
                raise PermissionError(
                    "Authentifizierung fehlgeschlagen – Benutzer oder Passwort falsch."
                )
            # Prüfe ob wir auf eine Login-Seite umgeleitet wurden
            if "j_security_check" in resp.url or "text/html" in resp.headers.get("Content-Type", ""):
                print("        WARNUNG: Möglicher Redirect auf Login-Seite!")
                print("        Versuche Formular-Authentifizierung...")
                self._form_login()

        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Keine Verbindung zum Server: {self.base_url}")

        # ② Service-Dokument laden (zeigt verfügbare Entity-Sets)
        print("  [2/5] Lade Service-Dokument...")
        try:
            resp = self._request(
                "GET",
                f"{self.odata_base}/ProdMgmt",
                timeout=30,
            )
            if resp.status_code == 200:
                try:
                    svc_doc = resp.json()
                    entity_sets = []
                    for item in svc_doc.get("value", []):
                        name = item.get("name", item.get("url", ""))
                        entity_sets.append(name)
                    if entity_sets:
                        print(f"        Entity-Sets: {', '.join(entity_sets[:15])}")
                        if len(entity_sets) > 15:
                            print(f"        ... und {len(entity_sets) - 15} weitere")
                except ValueError:
                    print("        (keine JSON-Antwort)")
        except Exception as e:
            print(f"        Fehler: {e}")

        # ③ Ersten Part laden um verfügbare Properties zu ermitteln
        print("  [3/5] Ermittle Part-Properties...")
        try:
            resp = self._request(
                "GET",
                f"{self.odata_base}/ProdMgmt/Parts",
                params={"$top": "1"},
                timeout=30,
            )

            if resp.status_code == 200:
                data = resp.json()
                items = data.get("value", [])
                if items:
                    self._part_properties = list(items[0].keys())
                    print(f"        Properties ({len(self._part_properties)}):")
                    for p in sorted(self._part_properties):
                        val = items[0][p]
                        val_preview = str(val)[:60] if val is not None else "null"
                        print(f"          {p}: {val_preview}")
                else:
                    print("        WARNUNG: Parts-Abfrage lieferte leere Liste!")
                    print(f"        Response: {resp.text[:300]}")
            else:
                print(f"        HTTP {resp.status_code}")
                print(f"        Response: {resp.text[:300]}")
        except Exception as e:
            print(f"        Fehler: {e}")

        # ④ Prüfe DocMgmt-Service für Dokument-Abfragen
        self._doc_service_available = False
        print("  [4/5] Prüfe DocMgmt-Service...")
        for doc_path in ["DocMgmt", "v6/DocMgmt", "DocMgmt/Documents"]:
            try:
                test_url = f"{self.odata_base}/{doc_path}"
                resp = self._request("GET", test_url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("value", [])
                    if items:
                        entity_sets = [it.get("name", it.get("url", "")) for it in items]
                        print(f"        → DocMgmt verfügbar ({doc_path}): {', '.join(entity_sets[:10])}")
                        self._doc_service_path = doc_path
                        self._doc_service_available = True
                        break
                    elif "ID" in str(data) or "Number" in str(data):
                        print(f"        → DocMgmt/Documents verfügbar ({doc_path})")
                        self._doc_service_path = doc_path
                        self._doc_service_available = True
                        break
                elif DEBUG:
                    print(f"        {doc_path}: HTTP {resp.status_code}")
            except Exception as e:
                if DEBUG:
                    print(f"        {doc_path}: {e}")
        if not self._doc_service_available:
            print("        DocMgmt-Service nicht verfügbar")

        # ⑤ Prüfe CADDocumentMgmt-Service (nur über v4 erreichbar)
        self._cad_service_available = False
        print("  [5/5] Prüfe CADDocumentMgmt-Service...")
        # CADDocumentMgmt existiert nur als v4-Service
        cad_base = self.base_url + "/servlet/odata/v4"
        for cad_path in ["CADDocumentMgmt", "CADDocumentMgmt/CADDocuments"]:
            try:
                test_url = f"{cad_base}/{cad_path}"
                resp = self._request("GET", test_url, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("value", [])
                    if items:
                        entity_sets = [it.get("name", it.get("url", "")) for it in items]
                        print(f"        → CADDocumentMgmt verfügbar ({cad_path} via v4): {', '.join(entity_sets[:10])}")
                        self._cad_service_available = True
                        break
                    elif "ID" in str(data) or "Number" in str(data):
                        print(f"        → CADDocumentMgmt/CADDocuments verfügbar (v4)")
                        self._cad_service_available = True
                        break
                elif DEBUG:
                    print(f"        {cad_path}: HTTP {resp.status_code}")
            except Exception as e:
                if DEBUG:
                    print(f"        {cad_path}: {e}")
        if not self._cad_service_available:
            print("        CADDocumentMgmt-Service nicht verfügbar")

        print()

    def _form_login(self):
        """Formular-basierte Authentifizierung (j_security_check) als Fallback."""
        login_url = f"{self.base_url}/j_security_check"
        data = {
            "j_username": self.username,
            "j_password": self.password,
        }
        try:
            resp = self._request(
                "POST",
                login_url,
                data=data,
                allow_redirects=True,
                timeout=30,
            )
            if DEBUG:
                print(f"        Form-Login Status: {resp.status_code}")
                print(f"        Form-Login URL: {resp.url}")
        except Exception as e:
            print(f"        Form-Login fehlgeschlagen: {e}")

    # ── HTTP-Hilfsmethoden ─────────────────────────────────────────────────
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Zentraler Request-Wrapper inkl. ausführlichem API-Logging."""
        started = time.perf_counter()
        method_upper = method.upper()

        def _redact(value):
            if isinstance(value, dict):
                masked = {}
                for key, entry in value.items():
                    k = str(key).lower()
                    if any(token in k for token in ("password", "passwd", "secret", "token")):
                        masked[key] = "***REDACTED***"
                    else:
                        masked[key] = entry
                return masked
            return value

        params = kwargs.get("params")
        payload_data = _redact(kwargs.get("data"))
        payload_json = _redact(kwargs.get("json"))
        timeout = kwargs.get("timeout", HTTP_TIMEOUT)
        allow_redirects = kwargs.get("allow_redirects", True)

        API_LOGGER.info(
            "REQ method=%s url=%s params=%s timeout=%s allow_redirects=%s data=%s json=%s",
            method_upper,
            url,
            params,
            timeout,
            allow_redirects,
            payload_data,
            payload_json,
        )

        try:
            with self._request_lock:
                resp = self.session.request(method_upper, url, **kwargs)

                nonce = resp.headers.get("CSRF_NONCE")
                if nonce:
                    self.session.headers["CSRF_NONCE"] = nonce

            elapsed_ms = (time.perf_counter() - started) * 1000
            content_type = resp.headers.get("Content-Type", "")

            body_preview = ""
            if "application/json" in content_type or "text/" in content_type:
                try:
                    body_preview = resp.text[:1000].replace("\n", "\\n")
                except Exception:
                    body_preview = "<body_unavailable>"

            API_LOGGER.info(
                "RES method=%s url=%s status=%s elapsed_ms=%.2f final_url=%s content_type=%s body_preview=%s",
                method_upper,
                url,
                resp.status_code,
                elapsed_ms,
                resp.url,
                content_type,
                body_preview,
            )
            return resp

        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000
            API_LOGGER.exception(
                "ERR method=%s url=%s elapsed_ms=%.2f error=%s",
                method_upper,
                url,
                elapsed_ms,
                exc,
            )
            raise

    def _get(
        self,
        url: str,
        params: dict = None,
        suppress_http_error_log: bool = False,
    ) -> requests.Response:
        """GET-Request mit Logging und Retry-Logik."""
        progress.tick_request()
        if DEBUG:
            param_str = "&".join(f"{k}={v}" for k, v in (params or {}).items())
            print(f"    GET {url}" + (f"?{param_str}" if param_str else ""))
        elif not progress.parts_total:
            # Im Non-Debug-Modus nur Statuszeile aktualisieren
            progress.print_status()

        last_exc = None
        for attempt in range(1, HTTP_RETRIES + 1):
            try:
                resp = self._request(
                    "GET",
                    url,
                    params=params,
                    timeout=HTTP_TIMEOUT,
                )

                if DEBUG and resp.status_code >= 400 and not suppress_http_error_log:
                    print(f"    → HTTP {resp.status_code}")
                    try:
                        err = resp.json()
                        msg = err.get("error", {}).get("message", "")
                        if isinstance(msg, dict):
                            msg = msg.get("value", str(msg))
                        print(f"    → Fehler: {msg}")
                    except Exception:
                        print(f"    → Body: {resp.text[:300]}")

                return resp

            except (requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError) as e:
                last_exc = e
                if attempt < HTTP_RETRIES:
                    wait = 2 ** attempt  # exponentielles Backoff: 2, 4, 8 …
                    print(f"    ⚠ Timeout/Verbindungsfehler (Versuch {attempt}/{HTTP_RETRIES}), "
                          f"warte {wait}s…")
                    time.sleep(wait)
                else:
                    print(f"    ✗ Endgültig fehlgeschlagen nach {HTTP_RETRIES} Versuchen.")
                    raise

    def _get_json(self, url: str, params: dict = None) -> dict:
        """GET-Request, gibt JSON-Antwort zurück."""
        resp = self._get(url, params)
        resp.raise_for_status()
        return resp.json()

    def _get_all_pages(self, url: str, params: dict = None) -> list:
        """Alle Seiten einer OData-Abfrage abrufen (Paginierung).
        Bricht nach MAX_PAGES Seiten ab, um Endlos-Paginierung zu vermeiden."""
        all_items = []
        page = 1
        data = self._get_json(url, params)
        all_items.extend(data.get("value", []))

        # Weitere Seiten laden (mit Seitenlimit)
        while "@odata.nextLink" in data:
            page += 1
            if page > MAX_PAGES:
                print(f"    ⚠ Seitenlimit ({MAX_PAGES}) erreicht – "
                      f"breche Paginierung ab ({len(all_items)} Einträge bisher).")
                break
            data = self._get_json(data["@odata.nextLink"])
            all_items.extend(data.get("value", []))

        return all_items

    def _try_get_all_pages(self, url: str, params: dict = None) -> list | None:
        """Wie _get_all_pages, gibt aber None bei HTTP-Fehlern zurück."""
        try:
            return self._get_all_pages(url, params)
        except requests.exceptions.HTTPError:
            return None

    # ── Part-Abfragen ──────────────────────────────────────────────────────
    def find_part(self, part_number: str) -> dict:
        """WTPart anhand der Nummer finden (neueste Version)."""
        return wt_parts.find_part(self, part_number, debug=DEBUG)

    def get_part_by_id(self, part_id: str) -> dict | None:
        """Part anhand seiner ID laden."""
        return wt_parts.get_part_by_id(self, part_id)

    def get_soft_attributes(self, part_id: str, attr_names: list[str]) -> dict:
        """Soft-Attribute (IBAs / kundenspezifische Attribute) eines Parts laden."""
        return wt_parts.get_soft_attributes(self, part_id, attr_names, debug=DEBUG)

    # ── BOM-Navigation ─────────────────────────────────────────────────────
    def get_bom_children(self, part_id: str) -> list:
        """BOM-Kinder eines Parts abrufen."""
        return wt_bom.get_bom_children(self, part_id, debug=DEBUG)

    def resolve_usage_link_child(self, link: dict) -> dict | None:
        """Child-Part aus einem UsageLink auflösen."""
        return wt_bom.resolve_usage_link_child(self, link)

    # ── Dokumenten-Abfragen ────────────────────────────────────────────────
    @staticmethod
    def _is_valid_document(doc: dict) -> bool:
        """Prüft ob ein Dokument-Objekt tatsächlich Daten enthält."""
        return wt_documents.is_valid_document(doc)

    def _get_part_reference_link_ids(self, part_id: str) -> set:
        """Holt die IDs aller WTPartReferenceLink-Objekte eines Parts."""
        return wt_documents.get_part_reference_link_ids(self, part_id, debug=DEBUG)

    def _doc_has_reference_link(self, doc_id: str, part_link_ids: set) -> bool:
        """Prüft ob ein Dokument über ReferencedBy einen der Part-Links hat."""
        return wt_documents.doc_has_reference_link(self, doc_id, part_link_ids, MAX_PAGES)

    def get_described_documents(self, part_id: str, part_number: str = "") -> list:
        """Dokumente die mit einem Part verknüpft sind."""
        return wt_documents.get_described_documents(
            self,
            part_id,
            part_number=part_number,
            debug=DEBUG,
        )

    def get_cad_documents(self, part_id: str) -> list:
        """CAD-Dokumente eines Parts abrufen."""
        return wt_documents.get_cad_documents(self, part_id, debug=DEBUG)

    # ── BOM-Baum aufbauen ──────────────────────────────────────────────────
    def build_bom_tree(
        self,
        part_number: str,
        depth: int = 0,
        visited: set = None,
        read_wt_documents: bool = True,
        read_cad_documents: bool = True,
    ) -> OrderedDict:
        """Rekursiv die BOM-Hierarchie aufbauen. Dokumente/CAD optional."""
        return wt_bom.build_bom_tree(
            self,
            part_number,
            progress=progress,
            max_bom_depth=MAX_BOM_DEPTH,
            depth=depth,
            visited=visited,
            read_wt_documents=read_wt_documents,
            read_cad_documents=read_cad_documents,
            debug=DEBUG,
        )


# ─── Statistik ────────────────────────────────────────────────────────────────
def count_tree(node: dict) -> dict:
    """Zählt Parts, Dokumente und CAD-Dokumente im Baum.
    Gibt ein dict mit detaillierter Aufschlüsselung zurück."""
    counts = {
        "parts": 1,
        "documents_total": 0,
        "documents_by_source": {},
        "cad_documents_total": 0,
        "cad_documents_by_source": {},
    }

    for doc in node.get("documents", []):
        counts["documents_total"] += 1
        src = doc.get("source", "unknown")
        counts["documents_by_source"][src] = counts["documents_by_source"].get(src, 0) + 1

    for cad in node.get("cad_documents", []):
        counts["cad_documents_total"] += 1
        src = cad.get("source", "unknown")
        counts["cad_documents_by_source"][src] = counts["cad_documents_by_source"].get(src, 0) + 1

    for child in node.get("children", []):
        child_counts = count_tree(child)
        counts["parts"] += child_counts["parts"]
        counts["documents_total"] += child_counts["documents_total"]
        counts["cad_documents_total"] += child_counts["cad_documents_total"]
        for src, cnt in child_counts["documents_by_source"].items():
            counts["documents_by_source"][src] = counts["documents_by_source"].get(src, 0) + cnt
        for src, cnt in child_counts["cad_documents_by_source"].items():
            counts["cad_documents_by_source"][src] = counts["cad_documents_by_source"].get(src, 0) + cnt

    return counts


def find_children_self_references(node: dict, path: str = "") -> list[dict]:
    """Findet Selbstreferenzen, bei denen ein Kind dieselbe Part-Nummer wie sein Parent hat."""
    findings = []

    if not isinstance(node, dict):
        return findings

    node_number = str(node.get("number", "")).strip()
    current_path = f"{path}/{node_number}" if path else node_number

    children = node.get("children", [])
    if isinstance(children, list):
        node_number_norm = node_number.upper() if node_number else ""
        for child in children:
            if not isinstance(child, dict):
                continue

            child_number = str(child.get("number", "")).strip()
            if node_number_norm and child_number and child_number.upper() == node_number_norm:
                findings.append({
                    "part_number": node_number,
                    "path": current_path,
                    "child_number": child_number,
                })

            findings.extend(find_children_self_references(child, current_path))

    return findings


# ─── Eingabe-Datei lesen ──────────────────────────────────────────────────────
def read_product_numbers(filepath: str) -> list[str]:
    """Liest Produktnummern zeilenweise aus einer Textdatei.
    Leere Zeilen und Kommentarzeilen (mit #) werden ignoriert."""
    abs_path = os.path.join(PROJECT_ROOT, filepath)
    if not os.path.isfile(abs_path):
        print(f"✗ Eingabedatei nicht gefunden: {abs_path}")
        sys.exit(1)

    products = []
    with open(abs_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                products.append(stripped)

    if not products:
        print(f"✗ Keine Produktnummern in {abs_path} gefunden.")
        sys.exit(1)

    return products


def export_single_product(client, product_number: str, username: str) -> bool:
    """Exportiert die BOM eines einzelnen Produkts als JSON. Gibt True bei Erfolg zurück."""
    global progress
    progress = ProgressTracker()

    print(f"\n{'═' * 64}")
    print(f"  Produkt: {product_number}")
    print(f"{'═' * 64}")

    # BOM auslesen
    print(f"Lese BOM-Struktur für {product_number}...")
    try:
        bom_tree = client.build_bom_tree(
            product_number,
            read_wt_documents=READ_WT_DOCUMENTS,
            read_cad_documents=READ_CAD_DOCUMENTS,
        )
    except Exception as e:
        progress.print_final_summary()
        print(f"\n✗ Fehler beim Auslesen der BOM für {product_number}: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Statistik
    progress.set_phase("Statistik")
    progress.print_status()
    stats = count_tree(bom_tree)
    self_ref_findings = find_children_self_references(bom_tree)
    self_ref_count = len(self_ref_findings)
    progress.print_final_summary()
    print(f"\n{'━' * 50}")
    print(f"  Parts:            {stats['parts']}")
    print(f"  Dokumente total:  {stats['documents_total']}")
    for src, cnt in sorted(stats["documents_by_source"].items()):
        print(f"    └─ {src}: {cnt}")
    print(f"  CAD-Dokumente:    {stats['cad_documents_total']}")
    for src, cnt in sorted(stats["cad_documents_by_source"].items()):
        print(f"    └─ {src}: {cnt}")
    print(f"  Selbstreferenzen (children):  {self_ref_count}")
    if self_ref_count:
        print("    ⚠ Gefundene Selbstreferenzen:")
        for finding in self_ref_findings[:10]:
            print(
                f"      - {finding['part_number']} in Pfad '{finding['path']}' "
                f"→ child '{finding['child_number']}'"
            )
    print(f"{'━' * 50}")

    # JSON erzeugen
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = OUTPUT_FILE.format(number=product_number, timestamp=timestamp)
    output_path = os.path.join(PROJECT_ROOT, output_filename)

    # Detaillierte Statistik für JSON
    stats_doc_detail = OrderedDict(sorted(stats["documents_by_source"].items()))
    stats_cad_detail = OrderedDict(sorted(stats["cad_documents_by_source"].items()))

    export_data = OrderedDict([
        ("export_info", OrderedDict([
            ("source_system", WINDCHILL_BASE_URL),
            ("odata_version", ODATA_VERSION),
            ("product_number", product_number),
            ("exported_by", username),
            ("export_timestamp", datetime.datetime.now().isoformat()),
            ("statistics", OrderedDict([
                ("total_parts", stats["parts"]),
                ("total_documents", stats["documents_total"]),
                ("documents_by_source", stats_doc_detail),
                ("total_cad_documents", stats["cad_documents_total"]),
                ("cad_documents_by_source", stats_cad_detail),
                ("children_self_references", self_ref_count),
            ])),
        ])),
        ("bom", bom_tree),
    ])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✓ Export gespeichert: {output_path}")
    return True


# ─── Hauptprogramm ───────────────────────────────────────────────────────────
def main():
    # Produktnummern aus input.txt lesen
    product_numbers = read_product_numbers(INPUT_FILE)

    print("=" * 64)
    print("  Windchill BOM Export Tool (Batch)")
    print(f"  Server:    {WINDCHILL_BASE_URL}")
    print(f"  Eingabe:   {INPUT_FILE}")
    print(f"  Produkte:  {len(product_numbers)}")
    for i, pn in enumerate(product_numbers, 1):
        print(f"    {i}. {pn}")
    print(f"  API:       OData {ODATA_VERSION}")
    print(f"  Debug:     {'EIN' if DEBUG else 'AUS'}")
    print("=" * 64)

    # Login-Daten abfragen (einmal für alle Produkte)
    username, password = get_credentials()
    if not username:
        print("\nLogin abgebrochen.")
        sys.exit(0)

    # Verbindung herstellen (einmal für alle Produkte)
    print(f"\nVerbinde als '{username}'...")
    try:
        client = WindchillClient(WINDCHILL_BASE_URL, username, password)
    except PermissionError as e:
        print(f"\n✗ {e}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"\n✗ {e}")
        sys.exit(1)

    print("Verbunden.")

    # Batch-Verarbeitung
    results = []  # (product_number, success)
    for idx, product_number in enumerate(product_numbers, 1):
        print(f"\n▶ [{idx}/{len(product_numbers)}] Verarbeite {product_number}...")
        success = export_single_product(client, product_number, username)
        results.append((product_number, success))

    # Zusammenfassung
    succeeded = sum(1 for _, ok in results if ok)
    failed = sum(1 for _, ok in results if not ok)

    print(f"\n\n{'═' * 64}")
    print(f"  BATCH-ZUSAMMENFASSUNG")
    print(f"{'─' * 64}")
    for pn, ok in results:
        status = "✓ OK" if ok else "✗ FEHLER"
        print(f"    {pn}  {status}")
    print(f"{'─' * 64}")
    print(f"  Erfolgreich: {succeeded}/{len(results)}")
    if failed:
        print(f"  Fehlgeschlagen: {failed}/{len(results)}")
    print(f"{'═' * 64}")
    print("  Fertig.")


if __name__ == "__main__":
    main()
