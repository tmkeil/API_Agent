"""
Business logic: Versions-/Iterationsverlauf und Lifecycle-History.

Service-Schicht zwischen Router und Adapter. Normalisiert OData-Rohdaten
zu typisierten DTOs.
"""

import logging
import time

from src.adapters.wrs_client import WRSClient
from src.core.odata import extract_id, normalize_item
from src.models.dto import (
    LifecycleEntry,
    LifecycleResponse,
    TimingInfo,
    VersionEntry,
    VersionsResponse,
)

logger = logging.getLogger(__name__)


def get_all_versions(
    client: WRSClient,
    type_key: str,
    code: str,
) -> VersionsResponse:
    """Alle Versionen/Iterationen eines Objekts laden."""
    t0 = time.monotonic()

    raw_items = client.get_all_versions(type_key, code)

    # Aktuelle (neueste) Version identifizieren
    current_id = ""
    if raw_items:
        # Die erste ist die neueste (bereits sortiert)
        current_id = extract_id(raw_items[0])

    versions = []
    for raw in raw_items:
        entry = _to_version_entry(raw)
        entry.isCurrent = (extract_id(raw) == current_id) if current_id else False
        versions.append(entry)

    ms = round((time.monotonic() - t0) * 1000, 1)
    return VersionsResponse(
        code=code,
        totalFound=len(versions),
        versions=versions,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def get_lifecycle_history(
    client: WRSClient,
    type_key: str,
    code: str,
) -> LifecycleResponse:
    """Lifecycle-History (Status-Uebergaenge) eines Objekts laden.

    Falls Windchill keinen LifeCycleHistory-Endpoint exponiert,
    wird aus der Versionsliste ein Pseudo-History abgeleitet.
    """
    t0 = time.monotonic()

    # Zuerst das Objekt finden um die ID zu bekommen
    raw_obj = client.find_object(type_key, code)
    obj_id = extract_id(raw_obj)

    events: list[LifecycleEntry] = []

    # Versuch 1: Echte Lifecycle-History vom Server
    if obj_id:
        raw_events = client.get_lifecycle_history(type_key, obj_id)
        for raw in raw_events:
            events.append(_to_lifecycle_entry(raw))

    # Versuch 2: Aus dem Versionsverlauf ableiten (Pseudo-History)
    if not events:
        raw_versions = client.get_all_versions(type_key, code)
        events = _derive_lifecycle_from_versions(raw_versions)

    ms = round((time.monotonic() - t0) * 1000, 1)
    return LifecycleResponse(
        code=code,
        totalFound=len(events),
        events=events,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def _to_version_entry(raw: dict) -> VersionEntry:
    """Normalize a raw OData dict to a VersionEntry DTO."""
    n = normalize_item(raw)
    return VersionEntry(
        objectId=n["id"],
        number=n["number"],
        name=n["name"],
        version=n["version"],
        iteration=n["iteration"],
        state=n["state"],
        identity=n["identity"],
        context=n["context"],
        lastModified=n["last_modified"],
        createdOn=n["created_on"],
    )


def _to_lifecycle_entry(raw: dict) -> LifecycleEntry:
    """Normalize a raw OData lifecycle event to a LifecycleEntry DTO."""
    from_state = str(
        raw.get("OldState") or raw.get("FromState") or raw.get("PreviousState") or ""
    )
    to_state = str(
        raw.get("NewState") or raw.get("ToState") or raw.get("State") or ""
    )
    # Unwrap state dicts
    if isinstance(raw.get("OldState"), dict):
        from_state = str(raw["OldState"].get("Value") or raw["OldState"].get("Display") or "")
    if isinstance(raw.get("NewState"), dict):
        to_state = str(raw["NewState"].get("Value") or raw["NewState"].get("Display") or "")

    timestamp = str(
        raw.get("Timestamp") or raw.get("ModifyTimestamp")
        or raw.get("EventDate") or raw.get("Date") or ""
    )
    user = str(
        raw.get("User") or raw.get("ModifiedBy") or raw.get("Actor") or ""
    )
    comment = str(raw.get("Comment") or raw.get("Note") or "")

    return LifecycleEntry(
        fromState=from_state,
        toState=to_state,
        timestamp=timestamp,
        user=user,
        comment=comment,
    )


def _derive_lifecycle_from_versions(raw_versions: list[dict]) -> list[LifecycleEntry]:
    """Pseudo-Lifecycle-History aus Versionsliste ableiten.

    Vergleicht aufeinanderfolgende Versionen und erzeugt Eintraege
    wenn sich der State aendert.
    """
    events: list[LifecycleEntry] = []

    # Aelteste zuerst (raw_versions ist neueste zuerst)
    versions = list(reversed(raw_versions))

    prev_state = ""
    for raw in versions:
        n = normalize_item(raw)
        state = n["state"]
        modified = n["last_modified"] or n["created_on"]

        if state and state != prev_state:
            events.append(LifecycleEntry(
                fromState=prev_state,
                toState=state,
                timestamp=modified,
                user="",
                comment=f"Version {n['version']}.{n['iteration']}",
            ))
            prev_state = state

    return events
