import datetime
import json
import os
import re
import secrets
import threading
import time
from collections import OrderedDict, deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

from flask import (
    Flask,
    g,
    jsonify,
    make_response,
    request,
    send_from_directory,
)

import windchill_modules.windchill_bom_export_app as _wc_module
from windchill_modules.windchill_bom_export_app import (
    OUTPUT_FILE,
    PROJECT_ROOT,
    WindchillClient,
    count_tree,
    find_children_self_references,
)
from windchill_modules.wt_bom import (
    MADE_FROM_INTERNAL_ATTRIBUTE_KEYS,
    MADE_FROM_USAGE_KEY_ALIASES,
)

# Reduce HTTP timeout/retries for the web tool (original: 120s / 3 retries)
_wc_module.HTTP_TIMEOUT = 30
_wc_module.HTTP_RETRIES = 2

SYSTEMS = {
    "prod": "https://plm-prod.neuhausen.balluff.net/Windchill",
    "test": "https://plm-test.neuhausen.balluff.net/Windchill",
    "dev": "https://plm-dev.neuhausen.balluff.net/Windchill",
}

SESSION_COOKIE = "wt_session"
SESSION_TTL_SECONDS = 60 * 60


@dataclass
class UserSession:
    token: str
    system_key: str
    system_url: str
    username: str
    client: WindchillClient
    expires_at: float
    part_by_id: dict[str, dict[str, Any]] = field(default_factory=dict)
    part_by_number: dict[str, dict[str, Any]] = field(default_factory=dict)
    bom_children_by_part: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    documents_by_part: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    cad_documents_by_part: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    made_from_by_part: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    search_cache: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    api_logs: deque[dict[str, Any]] = field(default_factory=lambda: deque(maxlen=500))
    lock: threading.Lock = field(default_factory=threading.Lock)


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, UserSession] = {}
        self._lock = threading.Lock()

    def put(self, session: UserSession) -> None:
        with self._lock:
            self._sessions[session.token] = session

    def get(self, token: str | None) -> UserSession | None:
        if not token:
            return None
        with self._lock:
            session = self._sessions.get(token)
            if not session:
                return None
            if session.expires_at < time.time():
                del self._sessions[token]
                return None
            session.expires_at = time.time() + SESSION_TTL_SECONDS
            return session

    def delete(self, token: str | None) -> None:
        if not token:
            return
        with self._lock:
            self._sessions.pop(token, None)


app = Flask(__name__, static_folder="static", static_url_path="")
session_store = SessionStore()


@app.before_request
def _request_timer_start() -> None:
    g.request_started_at = time.perf_counter()


@app.after_request
def _request_timer_end(response):
    started = getattr(g, "request_started_at", None)
    elapsed_ms = int((time.perf_counter() - started) * 1000) if started else -1
    print(
        f"[WEB] {request.method} {request.path} -> {response.status_code} ({elapsed_ms}ms)",
        flush=True,
    )
    return response


def _auth_error(message: str = "Nicht authentifiziert", status: int = 401):
    return jsonify({"error": message}), status


def _current_session() -> UserSession | None:
    token = request.cookies.get(SESSION_COOKIE)
    return session_store.get(token)


def _safe_filter_value(value: str) -> str:
    return value.replace("'", "''")


def _utc_timestamp() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()


def _log_session_event(
    session: UserSession,
    method: str,
    url: str,
    status: int,
    duration_ms: int,
    source: str,
    note: str = "",
) -> None:
    entry = {
        "timestamp": _utc_timestamp(),
        "source": source,
        "method": method,
        "url": url,
        "status": status,
        "durationMs": duration_ms,
        "note": note,
    }
    with session.lock:
        session.api_logs.appendleft(entry)


def _instrument_client_requests(session: UserSession) -> None:
    client = session.client
    if getattr(client, "_webtool_request_instrumented", False):
        return

    original_request = client._request

    def wrapped_request(method: str, url: str, **kwargs):
        start = time.perf_counter()
        try:
            response = original_request(method, url, **kwargs)
            duration_ms = int((time.perf_counter() - start) * 1000)
            _log_session_event(
                session,
                method=method.upper(),
                url=url,
                status=int(getattr(response, "status_code", 0) or 0),
                duration_ms=duration_ms,
                source="windchill",
            )
            return response
        except Exception as exc:  # noqa: BLE001
            duration_ms = int((time.perf_counter() - start) * 1000)
            _log_session_event(
                session,
                method=method.upper(),
                url=url,
                status=0,
                duration_ms=duration_ms,
                source="windchill",
                note=f"error: {exc}",
            )
            raise

    client._request = wrapped_request
    client._webtool_request_instrumented = True


def _part_from_cache_by_number(session: UserSession, part_number: str) -> dict[str, Any] | None:
    key = str(part_number).strip().upper()
    if not key:
        return None
    with session.lock:
        return session.part_by_number.get(key)


def _part_from_cache_by_id(session: UserSession, part_id: str) -> dict[str, Any] | None:
    key = str(part_id).strip()
    if not key:
        return None
    with session.lock:
        return session.part_by_id.get(key)


def _store_part_in_cache(session: UserSession, part: dict[str, Any]) -> None:
    part_id = str(part.get("ID") or part.get("id") or "").strip()
    number = str(part.get("Number") or part.get("PartNumber") or "").strip().upper()
    with session.lock:
        if part_id:
            session.part_by_id[part_id] = part
        if number:
            session.part_by_number[number] = part


def _get_part_by_number(session: UserSession, part_number: str) -> dict[str, Any]:
    cached = _part_from_cache_by_number(session, part_number)
    if cached is not None:
        _log_session_event(session, "CACHE", f"part:number:{part_number}", 200, 0, "cache", "part hit")
        return cached

    part = session.client.find_part(part_number)
    _store_part_in_cache(session, part)
    return part


def _get_part_by_id(session: UserSession, part_id: str) -> dict[str, Any] | None:
    cached = _part_from_cache_by_id(session, part_id)
    if cached is not None:
        _log_session_event(session, "CACHE", f"part:id:{part_id}", 200, 0, "cache", "part hit")
        return cached

    part = session.client.get_part_by_id(part_id)
    if part:
        _store_part_in_cache(session, part)
    return part


def _wildcard_to_regex(pattern: str) -> re.Pattern[str]:
    escaped = re.escape(pattern)
    escaped = escaped.replace(r"\*", ".*").replace(r"\?", ".")
    return re.compile(f"^{escaped}$", re.IGNORECASE)


def _match_score(query: str, number: str, name: str) -> tuple[int, str, str]:
    q = query.lower()
    number_l = (number or "").lower()
    name_l = (name or "").lower()

    if number_l == q:
        return (0, number_l, name_l)
    if name_l == q:
        return (1, number_l, name_l)
    if number_l.startswith(q):
        return (2, number_l, name_l)
    if name_l.startswith(q):
        return (3, number_l, name_l)
    if q in number_l:
        return (4, number_l, name_l)
    if q in name_l:
        return (5, number_l, name_l)
    return (9, number_l, name_l)


def _normalize_state(raw: Any) -> str:
    if isinstance(raw, dict):
        return str(raw.get("Value") or raw.get("Display") or "")
    return str(raw or "")


def _node_from_part(part: dict[str, Any], usage_link: dict[str, Any] | None = None) -> dict[str, Any]:
    part_id = part.get("ID") or part.get("id") or ""
    node = {
        "partId": part_id,
        "type": "WTPart",
        "number": part.get("Number") or part.get("PartNumber") or "",
        "name": part.get("Name") or part.get("DisplayName") or "",
        "version": str(part.get("Version") or part.get("VersionID") or ""),
        "iteration": str(part.get("Iteration") or part.get("IterationID") or ""),
        "state": _normalize_state(part.get("State") or part.get("LifeCycleState")),
        "identity": part.get("Identity") or part.get("DisplayIdentity") or "",
        "suffix": part.get("BALSUFFIX") or "",
        "binding": part.get("BALBINDING") or "",
        "isVariant": bool(part.get("BALISVARIANT")),
        "children": [],
        "documents": [],
        "cadDocuments": [],
        "expanded": False,
        "childrenLoaded": False,
        "hasChildren": bool(part_id),
    }

    if usage_link:
        quantity = usage_link.get("Quantity", 1)
        quantity_unit = ""
        if isinstance(quantity, dict):
            quantity_unit = str(quantity.get("Unit") or "")
            quantity = quantity.get("Value", 1)
        if not quantity_unit:
            raw_unit = usage_link.get("Unit") or usage_link.get("QuantityUnit") or ""
            if isinstance(raw_unit, dict):
                raw_unit = raw_unit.get("Value") or ""
            quantity_unit = str(raw_unit)

        usage_attributes = {}
        for key, value in usage_link.items():
            if key.startswith("@") or key in {"Quantity", "Unit", "LineNumber", "FindNumber", "Uses"}:
                continue
            if isinstance(value, (dict, list)):
                continue
            usage_attributes[key] = value

        node["quantity"] = quantity
        node["quantityUnit"] = quantity_unit
        node["lineNumber"] = str(usage_link.get("LineNumber") or usage_link.get("FindNumber") or "")
        node["usageAttributes"] = usage_attributes

    return node


def _node_from_document(doc: dict[str, Any], doc_type: str) -> dict[str, Any]:
    return {
        "partId": str(doc.get("ID") or ""),
        "type": doc_type,
        "number": doc.get("Number") or "",
        "name": doc.get("Name") or "",
        "version": str(doc.get("Version") or ""),
        "iteration": "",
        "state": _normalize_state(doc.get("State")),
        "identity": doc.get("Identity") or "",
        "suffix": "",
        "binding": "",
        "isVariant": False,
        "children": [],
        "documents": [],
        "cadDocuments": [],
        "expanded": False,
        "childrenLoaded": True,
        "hasChildren": False,
    }


def _normalize_made_from_numbers(raw_value: Any) -> list[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, dict):
        raw_value = raw_value.get("Value") or raw_value.get("Display") or ""
    if isinstance(raw_value, list):
        return [str(item).strip() for item in raw_value if str(item).strip()]
    text = str(raw_value).strip()
    if not text:
        return []
    return [text]


def _normalize_made_from_value(value: Any) -> Any:
    if isinstance(value, dict):
        return value.get("Value", value.get("Display", ""))
    if isinstance(value, list):
        compact = [v for v in value if v not in ("", None)]
        return compact[0] if compact else None
    return value


def _extract_made_from_relation_attributes(
    part: dict[str, Any],
    extra_attributes: dict[str, Any] | None = None,
) -> OrderedDict:
    relation_attributes: OrderedDict[str, Any] = OrderedDict()

    for key, value in part.items():
        upper = key.upper()
        if upper.startswith("BALMADEFROM") and upper != "BALMADEFROMNUMBER":
            normalized = _normalize_made_from_value(value)
            if normalized not in ("", None, []):
                relation_attributes[key] = normalized

    normalized_extra: dict[str, Any] = {}
    if extra_attributes:
        for key, value in extra_attributes.items():
            normalized = _normalize_made_from_value(value)
            if normalized in ("", None, []):
                continue
            normalized_extra[key] = normalized

    for canonical_key, aliases in MADE_FROM_USAGE_KEY_ALIASES.items():
        if canonical_key in relation_attributes:
            continue
        if canonical_key in normalized_extra:
            relation_attributes[canonical_key] = normalized_extra[canonical_key]
            continue
        for alias in aliases:
            if alias in normalized_extra:
                relation_attributes[canonical_key] = normalized_extra[alias]
                break

    for key, value in normalized_extra.items():
        if key not in relation_attributes:
            relation_attributes[key] = value

    return relation_attributes


def _build_made_from_nodes(session: UserSession, part: dict[str, Any]) -> list[dict[str, Any]]:
    client = session.client
    part_number = str(part.get("Number") or part.get("PartNumber") or "").strip().upper()
    part_id = str(part.get("ID") or part.get("id") or "")

    soft_attrs: dict[str, Any] = {}
    if part_id:
        try:
            soft_attrs = client.get_soft_attributes(part_id, MADE_FROM_INTERNAL_ATTRIBUTE_KEYS)
        except Exception:
            soft_attrs = {}

    relation_attrs = _extract_made_from_relation_attributes(part, soft_attrs)
    made_from_numbers = [
        number
        for number in _normalize_made_from_numbers(part.get("BALMADEFROMNUMBER", ""))
        if str(number).strip().upper() != part_number
    ]

    nodes: list[dict[str, Any]] = []
    for number in made_from_numbers:
        try:
            child_part = _get_part_by_number(session, str(number))
            child_node = _node_from_part(child_part)
        except Exception:
            child_node = {
                "partId": "",
                "type": "WTPart",
                "number": str(number),
                "name": "",
                "version": "",
                "iteration": "",
                "state": "",
                "identity": "",
                "suffix": "",
                "binding": "",
                "isVariant": False,
                "children": [],
                "documents": [],
                "cadDocuments": [],
                "expanded": False,
                "childrenLoaded": True,
                "hasChildren": False,
            }

        child_node["relationType"] = "madeFrom"
        child_node["usageAttributes"] = dict(relation_attrs)

        quantity = relation_attrs.get("BAL_SAP_STPO_ROANZ")
        quantity_unit = relation_attrs.get("BAL_SAP_STPO_ROAME")
        if quantity not in (None, ""):
            child_node["quantity"] = quantity
        if quantity_unit not in (None, ""):
            child_node["quantityUnit"] = str(quantity_unit)

        nodes.append(child_node)

    return nodes


def _frontend_tree_to_export(node: dict[str, Any]) -> OrderedDict:
    export_node = OrderedDict()
    export_node["action"] = "undefined"
    export_node["type"] = node.get("type", "WTPart")
    export_node["number"] = node.get("number", "")
    export_node["name"] = node.get("name", "")
    export_node["version"] = node.get("version", "")
    export_node["iteration"] = node.get("iteration", "")
    export_node["state"] = node.get("state", "")
    export_node["identity"] = node.get("identity", "")
    export_node["suffix"] = node.get("suffix", "")
    export_node["binding"] = node.get("binding", "")
    export_node["is_variant"] = bool(node.get("isVariant", False))

    usage_attributes = node.get("usageAttributes") or {}
    if usage_attributes:
        export_node["usage_attributes"] = usage_attributes

    if "quantity" in node:
        export_node["quantity"] = node.get("quantity")
    if "quantityUnit" in node:
        export_node["quantity_unit"] = node.get("quantityUnit", "")
    if node.get("lineNumber"):
        export_node["line_number"] = node.get("lineNumber")

    children = []
    for child in node.get("children", []):
        children.append(_frontend_tree_to_export(child))

    documents = []
    for doc in node.get("documents", []):
        documents.append(
            OrderedDict(
                [
                    ("type", "WTDocument"),
                    ("number", doc.get("number", "")),
                    ("name", doc.get("name", "")),
                    ("version", doc.get("version", "")),
                    ("state", doc.get("state", "")),
                    ("identity", doc.get("identity", "")),
                ]
            )
        )

    cad_documents = []
    for cad in node.get("cadDocuments", []):
        cad_documents.append(
            OrderedDict(
                [
                    ("type", "CADDocument"),
                    ("number", cad.get("number", "")),
                    ("name", cad.get("name", "")),
                    ("version", cad.get("version", "")),
                    ("state", cad.get("state", "")),
                    ("identity", cad.get("identity", "")),
                ]
            )
        )

    export_node["children_type"] = "subassembly" if children else "no additional children"
    export_node["children"] = children
    export_node["documents"] = documents
    export_node["cad_documents"] = cad_documents
    return export_node


def _write_export_file(product_number: str, export_data: OrderedDict) -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = OUTPUT_FILE.format(number=product_number, timestamp=timestamp)
    output_path = os.path.join(PROJECT_ROOT, output_filename)

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(export_data, handle, indent=2, ensure_ascii=False, default=str)

    return output_filename


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/systems")
def systems():
    return jsonify(
        {
            "systems": [
                {"key": key, "label": key.upper(), "url": url + "/app/"}
                for key, url in SYSTEMS.items()
            ]
        }
    )


@app.post("/api/login")
def login():
    payload = request.get_json(silent=True) or {}
    system_key = str(payload.get("system") or "").strip().lower()
    username = str(payload.get("username") or "").strip()
    password = str(payload.get("password") or "")

    if system_key not in SYSTEMS:
        return jsonify({"error": "Ungültiges Zielsystem"}), 400
    if not username or not password:
        return jsonify({"error": "Benutzername und Passwort erforderlich"}), 400

    try:
        client = WindchillClient(SYSTEMS[system_key], username, password)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Login fehlgeschlagen: {exc}"}), 401

    token = secrets.token_urlsafe(32)
    session = UserSession(
        token=token,
        system_key=system_key,
        system_url=SYSTEMS[system_key],
        username=username,
        client=client,
        expires_at=time.time() + SESSION_TTL_SECONDS,
    )
    _instrument_client_requests(session)
    _log_session_event(session, "LOGIN", "/api/login", 200, 0, "web", "session started")
    session_store.put(session)

    response = make_response(
        jsonify(
            {
                "ok": True,
                "system": system_key,
                "systemUrl": SYSTEMS[system_key],
                "username": username,
            }
        )
    )
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=False,
        samesite="Strict",
        max_age=SESSION_TTL_SECONDS,
    )
    return response


@app.post("/api/logout")
def logout():
    token = request.cookies.get(SESSION_COOKIE)
    session_store.delete(token)

    response = make_response(jsonify({"ok": True}))
    response.delete_cookie(SESSION_COOKIE)
    return response


@app.get("/api/me")
def me():
    session = _current_session()
    if not session:
        return _auth_error()

    return jsonify(
        {
            "ok": True,
            "username": session.username,
            "system": session.system_key,
            "systemUrl": session.system_url,
        }
    )


@app.get("/api/search")
def search_parts():
    session = _current_session()
    if not session:
        return _auth_error()

    query = str(request.args.get("q") or "").strip()
    if not query:
        return jsonify({"items": []})

    limit = min(max(int(request.args.get("limit", 25)), 1), 100)
    client = session.client

    cache_key = f"{query.lower()}|{limit}"
    with session.lock:
        cached_matches = session.search_cache.get(cache_key)
    if cached_matches is not None:
        _log_session_event(session, "CACHE", f"search:{query}", 200, 0, "cache", "search hit")
        return jsonify({"items": cached_matches})
    url = f"{client.odata_base}/ProdMgmt/Parts"

    collected: dict[str, dict[str, Any]] = {}
    wildcard = "*" in query or "?" in query
    regex = _wildcard_to_regex(query)

    core = query.replace("*", "").replace("?", "").strip()
    candidates = []

    if core:
        safe_core = _safe_filter_value(core)
        candidates.extend(
            [
                {"$filter": f"contains(Number,'{safe_core}')", "$top": "100"},
                {"$filter": f"contains(Name,'{safe_core}')", "$top": "100"},
            ]
        )

    if not wildcard:
        safe_q = _safe_filter_value(query)
        candidates.insert(0, {"$filter": f"Number eq '{safe_q}'", "$top": "20"})

    for params in candidates:
        try:
            items = client._get_all_pages(url, params)
        except Exception:
            continue
        for item in items:
            part_id = item.get("ID") or item.get("id")
            if part_id:
                collected[str(part_id)] = item
            if len(collected) >= 250:
                break
        if len(collected) >= 250:
            break

    if not collected:
        try:
            for item in client._get_all_pages(url, {"$top": "200"}):
                part_id = item.get("ID") or item.get("id")
                if part_id:
                    collected[str(part_id)] = item
        except Exception:
            return jsonify({"error": "Suche im Windchill-System fehlgeschlagen"}), 502

    matches = []
    for part in collected.values():
        number = str(part.get("Number") or part.get("PartNumber") or "")
        name = str(part.get("Name") or "")

        text_match = regex.search(number) or regex.search(name)
        if not text_match:
            if not wildcard and core.lower() in (number + " " + name).lower():
                text_match = True
            elif wildcard:
                text_match = False

        if not text_match:
            continue

        matches.append(
            {
                "partId": part.get("ID") or part.get("id") or "",
                "number": number,
                "name": name,
                "version": str(part.get("Version") or part.get("VersionID") or ""),
                "iteration": str(part.get("Iteration") or part.get("IterationID") or ""),
                "state": _normalize_state(part.get("State") or part.get("LifeCycleState")),
                "identity": part.get("Identity") or "",
            }
        )

    matches.sort(key=lambda item: _match_score(query, item["number"], item["name"]))
    result_items = matches[:limit]
    with session.lock:
        session.search_cache[cache_key] = result_items
    return jsonify({"items": result_items})


@app.get("/api/bom/root")
def bom_root():
    session = _current_session()
    if not session:
        return _auth_error()

    part_number = str(request.args.get("partNumber") or "").strip()
    if not part_number:
        return jsonify({"error": "partNumber fehlt"}), 400

    try:
        part = _get_part_by_number(session, part_number)
        node = _node_from_part(part)
        node["hasChildren"] = bool(node.get("partId"))

        return jsonify({"root": node})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Part konnte nicht geladen werden: {exc}"}), 404


@app.get("/api/bom/children")
def bom_children():
    session = _current_session()
    if not session:
        return _auth_error()

    part_id = str(request.args.get("partId") or "").strip()
    if not part_id:
        return jsonify({"error": "partId fehlt"}), 400

    expand_started = time.perf_counter()
    print(f"[EXPAND] start partId={part_id}", flush=True)

    client = session.client
    children_from_cache = False
    made_from_from_cache = False
    docs_from_cache = False
    cad_from_cache = False

    try:
        part = _get_part_by_id(session, part_id)
    except Exception as exc:  # noqa: BLE001
        print(f"[EXPAND] error partId={part_id} step=part-read error={exc}", flush=True)
        return jsonify({"error": f"Part konnte nicht gelesen werden: {exc}"}), 502

    with session.lock:
        links = session.bom_children_by_part.get(part_id)
    if links is None:
        try:
            links = client.get_bom_children(part_id)
        except Exception as exc:  # noqa: BLE001
            print(f"[EXPAND] error partId={part_id} step=children-read error={exc}", flush=True)
            return jsonify({"error": f"Kinder konnten nicht gelesen werden: {exc}"}), 502
        with session.lock:
            session.bom_children_by_part[part_id] = links
    else:
        children_from_cache = True
        _log_session_event(session, "CACHE", f"bom:children:{part_id}", 200, 0, "cache", "children hit")

    made_from_nodes: list[dict[str, Any]] = []
    documents: list[dict[str, Any]] = []
    cad_documents: list[dict[str, Any]] = []

    _SENTINEL = object()  # distinguish "not cached" from "cached empty list"

    # ── Determine which tasks need fresh API calls ─────────────
    need_made_from = False
    need_docs = False
    need_cad = False

    if part:
        with session.lock:
            mf_cached = session.made_from_by_part.get(part_id, _SENTINEL)
        if mf_cached is _SENTINEL:
            need_made_from = True
        else:
            made_from_nodes = mf_cached
            made_from_from_cache = True
            _log_session_event(session, "CACHE", f"bom:madefrom:{part_id}", 200, 0, "cache", "made-from hit")
            print(f"[EXPAND]   madeFrom cache hit={len(made_from_nodes)}", flush=True)

        with session.lock:
            docs_cached = session.documents_by_part.get(part_id, _SENTINEL)
        if docs_cached is _SENTINEL:
            need_docs = True
        else:
            documents = docs_cached
            docs_from_cache = True
            _log_session_event(session, "CACHE", f"bom:documents:{part_id}", 200, 0, "cache", "documents hit")
            print(f"[EXPAND]   documents cache hit={len(documents)}", flush=True)

        with session.lock:
            cad_cached = session.cad_documents_by_part.get(part_id, _SENTINEL)
        if cad_cached is _SENTINEL:
            need_cad = True
        else:
            cad_documents = cad_cached
            cad_from_cache = True
            _log_session_event(session, "CACHE", f"bom:cad:{part_id}", 200, 0, "cache", "cad hit")
            print(f"[EXPAND]   cad cache hit={len(cad_documents)}", flush=True)

    # ── Parallel loading: made-from, documents, CAD, child resolution ──
    def _load_made_from():
        t0 = time.perf_counter()
        try:
            nodes = _build_made_from_nodes(session, part)
            with session.lock:
                session.made_from_by_part[part_id] = nodes
        except Exception:
            nodes = []
        ms = int((time.perf_counter() - t0) * 1000)
        print(f"[EXPAND]   madeFrom loaded={len(nodes)} elapsed={ms}ms", flush=True)
        return ("made_from", nodes)

    def _load_documents():
        t0 = time.perf_counter()
        try:
            docs_raw = client.get_described_documents(part_id, part_number=str(part.get("Number") or ""))
            docs = [_node_from_document(doc, "WTDocument") for doc in docs_raw]
            with session.lock:
                session.documents_by_part[part_id] = docs
        except Exception:
            docs = []
        ms = int((time.perf_counter() - t0) * 1000)
        print(f"[EXPAND]   documents loaded={len(docs)} elapsed={ms}ms", flush=True)
        return ("documents", docs)

    def _load_cad():
        t0 = time.perf_counter()
        try:
            cad_raw = client.get_cad_documents(part_id)
            cads = [_node_from_document(doc, "CADDocument") for doc in cad_raw]
            with session.lock:
                session.cad_documents_by_part[part_id] = cads
        except Exception:
            cads = []
        ms = int((time.perf_counter() - t0) * 1000)
        print(f"[EXPAND]   cad loaded={len(cads)} elapsed={ms}ms", flush=True)
        return ("cad", cads)

    def _resolve_child(link):
        child = client.resolve_usage_link_child(link)
        if not child:
            return None
        child_id = child.get("ID") or child.get("id") or ""
        if child_id:
            with session.lock:
                session.part_by_id[child_id] = child
        child_node = _node_from_part(child, usage_link=link)
        child_node["hasChildren"] = bool(child_node.get("partId"))
        return child_node

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}

        if need_made_from:
            futures[executor.submit(_load_made_from)] = "made_from"
        if need_docs:
            futures[executor.submit(_load_documents)] = "documents"
        if need_cad:
            futures[executor.submit(_load_cad)] = "cad"

        # Resolve children in parallel
        step_t = time.perf_counter()
        child_futures = [executor.submit(_resolve_child, link) for link in links]

        # Collect metadata results
        for future in as_completed(futures):
            key, result = future.result()
            if key == "made_from":
                made_from_nodes = result
            elif key == "documents":
                documents = result
            elif key == "cad":
                cad_documents = result

        # Collect resolved children (preserve order)
        children = []
        for future in child_futures:
            node = future.result()
            if node is not None:
                children.append(node)

    children.sort(key=lambda item: (item.get("lineNumber", ""), item.get("number", "")))
    print(f"[EXPAND]   children resolved={len(children)}/{len(links)} elapsed={int((time.perf_counter()-step_t)*1000)}ms", flush=True)

    elapsed_ms = int((time.perf_counter() - expand_started) * 1000)
    print(
        "[EXPAND] done "
        f"partId={part_id} "
        f"partNumber={str(part.get('Number') or part.get('PartNumber') or '?') if part else '?'} "
        f"children={len(children)} docs={len(documents)} cad={len(cad_documents)} madeFrom={len(made_from_nodes)} "
        f"cache(children={children_from_cache},madeFrom={made_from_from_cache},docs={docs_from_cache},cad={cad_from_cache}) "
        f"elapsed={elapsed_ms}ms",
        flush=True,
    )

    return jsonify(
        {
            "items": made_from_nodes + children,
            "documents": documents,
            "cadDocuments": cad_documents,
        }
    )


@app.get("/api/logs")
def api_logs():
    session = _current_session()
    if not session:
        return _auth_error()

    limit = min(max(int(request.args.get("limit", 120)), 1), 500)
    with session.lock:
        items = list(session.api_logs)[:limit]
    return jsonify({"items": items})


@app.post("/api/export")
def export_bom():
    session = _current_session()
    if not session:
        return _auth_error()

    payload = request.get_json(silent=True) or {}
    mode = str(payload.get("mode") or "expandedOnly")
    part_number = str(payload.get("partNumber") or "").strip()

    if not part_number:
        return jsonify({"error": "partNumber fehlt"}), 400

    if mode not in {"expandedOnly", "fullTree"}:
        return jsonify({"error": "Ungültiger Exportmodus"}), 400

    if mode == "fullTree":
        try:
            bom_tree = session.client.build_bom_tree(part_number)
        except Exception as exc:  # noqa: BLE001
            return jsonify({"error": f"Vollständiger Export fehlgeschlagen: {exc}"}), 502
    else:
        root_tree = payload.get("tree")
        if not isinstance(root_tree, dict):
            return jsonify({"error": "Für expandedOnly ist ein Tree-Objekt erforderlich"}), 400
        bom_tree = _frontend_tree_to_export(root_tree)

    stats = count_tree(bom_tree)
    self_refs = find_children_self_references(bom_tree)

    export_data = OrderedDict(
        [
            (
                "export_info",
                OrderedDict(
                    [
                        ("source_system", session.system_url),
                        ("odata_version", "v6"),
                        ("product_number", part_number),
                        ("exported_by", session.username),
                        ("export_timestamp", datetime.datetime.now().isoformat()),
                        (
                            "statistics",
                            OrderedDict(
                                [
                                    ("total_parts", stats["parts"]),
                                    ("total_documents", stats["documents_total"]),
                                    (
                                        "documents_by_source",
                                        OrderedDict(sorted(stats["documents_by_source"].items())),
                                    ),
                                    ("total_cad_documents", stats["cad_documents_total"]),
                                    (
                                        "cad_documents_by_source",
                                        OrderedDict(sorted(stats["cad_documents_by_source"].items())),
                                    ),
                                    ("children_self_references", len(self_refs)),
                                ]
                            ),
                        ),
                    ]
                ),
            ),
            ("bom", bom_tree),
        ]
    )

    filename = _write_export_file(part_number, export_data)
    return jsonify(
        {
            "ok": True,
            "filename": filename,
            "downloadUrl": f"/api/export/download/{filename}",
        }
    )


@app.get("/api/export/download/<path:filename>")
def export_download(filename: str):
    session = _current_session()
    if not session:
        return _auth_error()

    safe_name = os.path.basename(filename)
    return send_from_directory(PROJECT_ROOT, safe_name, as_attachment=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
