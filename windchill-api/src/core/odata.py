"""
Zentrale OData-Normalisierung fuer Windchill WRS-Responses.

Windchill WRS liefert je nach Endpoint, $expand und OData-Version
unterschiedliche Feldnamen (z.B. "ID" vs "id", "Number" vs "PartNumber").
Dieses Modul loest alle Aliase EINMAL auf und eliminiert die 30+
.get()-Fallback-Ketten, die sich vorher durch den gesamten Code zogen.

Ausserdem: Windchill-Typ-Konstanten und Such-Ranking.
"""

from enum import IntEnum
from typing import Any


# ── OData Field Aliases ──────────────────────────────────────
#
# canonical_key → list of OData field names (tried left to right)

_FIELD_ALIASES: dict[str, list[str]] = {
    "id":            ["ID", "id"],
    "number":        ["Number", "PartNumber"],
    "name":          ["Name", "DisplayName"],
    "version":       ["Version", "VersionID"],
    "iteration":     ["Iteration", "IterationID"],
    "state":         ["State", "LifeCycleState"],
    "identity":      ["Identity", "DisplayIdentity"],
    "context":       ["ContainerName", "FolderLocation"],
    "last_modified": ["LastModified", "ModifyTimestamp"],
    "created_on":    ["CreatedOn", "CreateTimestamp"],
    "is_variant":    ["IsVariant", "BALISVARIANT", "Variant"],
    "organization_id": ["OrganizationName", "Context", "OrganizationUniqueIdentifier", "OrganizationID", "Organization"],
    "classification": ["TypeName", "Classification", "SubType"],
}


# ── Boolean normalization ────────────────────────────────────

_BOOL_MAP: dict[str, str] = {
    "true": "Yes", "yes": "Yes", "1": "Yes",
    "false": "No", "no": "No", "0": "No",
}


# ── Normalization helpers ────────────────────────────────────


def normalize_state(raw: Any) -> str:
    """Unwrap State-Dicts ({Value: …, Display: …}) zu einem Plain-String."""
    if isinstance(raw, dict):
        return str(raw.get("Value") or raw.get("Display") or "")
    return str(raw or "")


def extract_id(raw: dict) -> str:
    """Objekt-ID aus einem OData-Dict extrahieren (ID oder id)."""
    return str(raw.get("ID") or raw.get("id") or "")


def normalize_item(raw: dict) -> dict:
    """Alle OData-Feld-Aliase in kanonische Keys aufloesen.

    Returns:
        Dict mit den Keys: id, number, name, version, iteration,
        state (bereits entpackt), identity, context, last_modified,
        created_on.  Plus _entity_type / _entity_type_key falls vorhanden.
    """
    result: dict[str, Any] = {}

    for canonical, aliases in _FIELD_ALIASES.items():
        value = None
        for alias in aliases:
            value = raw.get(alias)
            if value is not None:
                break
        if canonical == "state":
            result[canonical] = normalize_state(value)
        elif canonical == "is_variant":
            if value is None or value == "":
                result[canonical] = ""
            elif isinstance(value, bool):
                result[canonical] = "Yes" if value else "No"
            else:
                result[canonical] = _BOOL_MAP.get(str(value).lower(), str(value))
        else:
            result[canonical] = str(value) if value is not None else ""

    # Fallback fuer Context: aus FolderLocation oder ContainerReference extrahieren
    if not result.get("context"):
        cref = raw.get("ContainerReference")
        if isinstance(cref, dict):
            result["context"] = str(
                cref.get("Name") or cref.get("DisplayName") or ""
            )
    # FolderLocation → Kontext = erster Pfad-Abschnitt
    ctx = result.get("context", "")
    if ctx.startswith("/"):
        parts = ctx.strip("/").split("/")
        result["context"] = parts[0] if parts else ctx

    # Injizierte Metadaten beibehalten (von SearchMixin)
    for meta_key in ("_entity_type", "_entity_type_key"):
        if meta_key in raw:
            result[meta_key] = raw[meta_key]

    return result


# ── Windchill Type Constants ─────────────────────────────────


class WcType:
    """Windchill-Objekttyp-Bezeichner als Konstanten."""
    PART = "WTPart"
    DOCUMENT = "WTDocument"
    EPM_DOCUMENT = "EPMDocument"
    CAD_DOCUMENT = "CADDocument"
    CHANGE_NOTICE = "WTChangeOrder2"
    CHANGE_REQUEST = "WTChangeRequest2"
    PROBLEM_REPORT = "WTChangeIssue"


# ── Search Result Ranking ────────────────────────────────────


class MatchRank(IntEnum):
    """Prioritaetsstufen fuer Suchergebnis-Ranking (niedriger = besser)."""
    EXACT_NUMBER   = 0
    EXACT_NAME     = 1
    NUMBER_PREFIX  = 2
    NAME_PREFIX    = 3
    NUMBER_CONTAINS = 4
    NAME_CONTAINS  = 5
    NO_MATCH       = 9


def match_score(query: str, number: str, name: str) -> tuple:
    """Suchergebnis bewerten fuer Sortierung. Niedrigerer Wert = besserer Treffer.

    Returns:
        Tuple (MatchRank, number_lower, name_lower) als sort-key.
    """
    q = query.lower()
    num = (number or "").lower()
    nam = (name or "").lower()

    if num == q:
        return (MatchRank.EXACT_NUMBER, num, nam)
    if nam == q:
        return (MatchRank.EXACT_NAME, num, nam)
    if num.startswith(q):
        return (MatchRank.NUMBER_PREFIX, num, nam)
    if nam.startswith(q):
        return (MatchRank.NAME_PREFIX, num, nam)
    if q in num:
        return (MatchRank.NUMBER_CONTAINS, num, nam)
    if q in nam:
        return (MatchRank.NAME_CONTAINS, num, nam)
    return (MatchRank.NO_MATCH, num, nam)
