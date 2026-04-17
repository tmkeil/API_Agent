"""
WorkItem Service — Projektfortschritt-Tracking.

Speichert WorkItems als JSON-Dateien im Dateisystem.
Jedes WorkItem dokumentiert den Arbeitsablauf:
  CN auswählen → Parts laden → Part wählen → BOM exportieren → bearbeiten → CSV erzeugen.
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from src.models.dto import WorkItem, WorkItemListResponse, WorkItemStep, WorkItemSummary

logger = logging.getLogger(__name__)

# Storage-Verzeichnis (konfigurierbar via Env)
_STORAGE_DIR = Path(os.getenv("WORKITEM_STORAGE_DIR", "data/workitems"))


def _ensure_dir() -> Path:
    _STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    return _STORAGE_DIR


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(workitem_id: str) -> dict | None:
    path = _ensure_dir() / f"{workitem_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _save(data: dict) -> None:
    path = _ensure_dir() / f"{data['id']}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ── CRUD ─────────────────────────────────────────────────────


def create_workitem(cn_data: dict) -> WorkItem:
    """Neues WorkItem anlegen wenn ein CN ausgewaehlt wird."""
    now = _now_iso()
    wi = {
        "id": str(uuid.uuid4())[:8],
        "status": "in_progress",
        "createdAt": now,
        "updatedAt": now,
        "changeNotice": cn_data,
        "resultingParts": [],
        "selectedPart": {},
        "bomData": [],
        "bomColumns": [],
        "steps": [
            {
                "step": "cn_selected",
                "timestamp": now,
                "data": {"cnNumber": cn_data.get("number", "")},
            }
        ],
    }
    _save(wi)
    logger.info("WorkItem %s erstellt fuer CN %s", wi["id"], cn_data.get("number", ""))
    return WorkItem(**wi)


def get_workitem(workitem_id: str) -> WorkItem | None:
    """WorkItem laden."""
    data = _load(workitem_id)
    if data is None:
        return None
    return WorkItem(**data)


def list_workitems() -> WorkItemListResponse:
    """Alle WorkItems auflisten."""
    storage = _ensure_dir()
    items: list[WorkItemSummary] = []
    for path in sorted(storage.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            cn = data.get("changeNotice", {})
            items.append(WorkItemSummary(
                id=data["id"],
                cnNumber=cn.get("number", ""),
                cnName=cn.get("name", ""),
                cnSubType=cn.get("subType", ""),
                status=data.get("status", "in_progress"),
                createdAt=data.get("createdAt", ""),
                updatedAt=data.get("updatedAt", ""),
                stepCount=len(data.get("steps", [])),
            ))
        except Exception:
            logger.debug("Fehler beim Laden von %s", path, exc_info=True)

    return WorkItemListResponse(items=items, totalCount=len(items))


def add_step(workitem_id: str, step: str, data: dict | None = None) -> WorkItem | None:
    """Arbeitsschritt hinzufuegen."""
    wi_data = _load(workitem_id)
    if wi_data is None:
        return None

    now = _now_iso()
    wi_data["steps"].append({
        "step": step,
        "timestamp": now,
        "data": data or {},
    })
    wi_data["updatedAt"] = now
    _save(wi_data)
    return WorkItem(**wi_data)


def update_workitem(workitem_id: str, updates: dict) -> WorkItem | None:
    """WorkItem-Felder aktualisieren (resultingParts, selectedPart, bomData, bomColumns, status)."""
    wi_data = _load(workitem_id)
    if wi_data is None:
        return None

    allowed = {"resultingParts", "selectedPart", "bomData", "bomColumns", "status"}
    for key, value in updates.items():
        if key in allowed:
            wi_data[key] = value

    wi_data["updatedAt"] = _now_iso()
    _save(wi_data)
    return WorkItem(**wi_data)


def delete_workitem(workitem_id: str) -> bool:
    """WorkItem loeschen."""
    path = _ensure_dir() / f"{workitem_id}.json"
    if path.exists():
        path.unlink()
        logger.info("WorkItem %s geloescht", workitem_id)
        return True
    return False
