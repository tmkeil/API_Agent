"""BOM Transformer service — Phase 1 read-only dual-tree view.

Loads, in a single backend call, both the Design-side and Manufacturing-side
BOM root nodes plus the Equivalence Network for a given Part code. The
frontend then lazy-loads children per side via the existing /bom/children
endpoint, exactly as the StructureTab does.

Phase 2 (write) lives in adapters/bom_transformation_mixin.py.
"""

import logging
import time
from typing import Optional

from src.adapters.wrs_client import WRSClient
from src.core.session import UserSession, log_session_event
from src.models.dto import (
    BomTransformerResponse,
    BomTreeNode,
    EquivalenceNetworkResponse,
    EquivPartRef,
    TimingInfo,
    TransformResponse,
    TransformRemoveResponse,
)
from src.services import parts_service

logger = logging.getLogger(__name__)


def _pick_counterpart(refs: list[EquivPartRef]) -> Optional[str]:
    """Pick the first usable Part-Number from a list of equivalence refs."""
    for r in refs:
        if r.number:
            return r.number
    return None


def _safe_root(
    client: WRSClient,
    code: Optional[str],
    session: Optional[UserSession],
) -> Optional[BomTreeNode]:
    """Best-effort BOM root load; return None on any failure."""
    if not code:
        return None
    try:
        return parts_service.get_bom_root(client, code, session=session)
    except Exception as exc:  # noqa: BLE001 — keep transformer view tolerant
        logger.warning("bom_transformer: root load failed for %r: %s", code, exc)
        if session:
            log_session_event(
                session, "WARN", f"transformer:root:{code}", 0, 0, "service",
                f"root load failed: {exc}",
            )
        return None


def get_transformer_view(
    client: WRSClient,
    code: str,
    session: Optional[UserSession] = None,
) -> BomTransformerResponse:
    """Load Design+Manufacturing BOM roots and the Equivalence Network.

    Strategy:
      1. Load equivalence network for `code` (resolves selfView and counterparts).
      2. Depending on selfView, place `code` on the matching side and pick the
         first counterpart (down[0] or up[0]) for the opposite side.
      3. Load BOM roots for both sides (best-effort).
    """
    t0 = time.monotonic()

    equivalence = parts_service.get_part_equivalence(client, code)
    self_view = (equivalence.selfView or "").strip()

    design_code: Optional[str] = None
    mfg_code: Optional[str] = None

    if self_view.lower().startswith("manuf"):
        # `code` is the Manufacturing side — design parent is in `up`
        mfg_code = code
        design_code = _pick_counterpart(equivalence.up)
    else:
        # Treat anything non-Manufacturing (Design / unknown) as Design side
        design_code = code
        mfg_code = _pick_counterpart(equivalence.down)

    design_root = _safe_root(client, design_code, session)
    mfg_root = _safe_root(client, mfg_code, session)

    ms = round((time.monotonic() - t0) * 1000, 1)
    return BomTransformerResponse(
        code=code,
        selfView=self_view,
        designRoot=design_root,
        manufacturingRoot=mfg_root,
        equivalence=equivalence,
        timing=TimingInfo(totalMs=ms, wrsMs=equivalence.timing.wrsMs),
    )


# ── Phase 2b — Discrepancy detection & downstream generation ──


def detect_discrepancies(
    client: WRSClient,
    target_path: str,
    source_part_paths: list[str] | None = None,
    upstream_change_oid: str = "",
    session: Optional[UserSession] = None,
) -> TransformResponse:
    """Wrapper around ``client.detect_discrepancies`` returning a TransformResponse.

    Bubbles the raw OData ``value`` array back to the caller without
    interpretation — the exact shape of discrepancy items is documented
    in the BomTransformation Swagger and may differ slightly between
    Windchill versions.
    """
    t0 = time.monotonic()
    raw = client.detect_discrepancies(
        target_path=target_path,
        source_part_paths=source_part_paths or None,
        upstream_change_oid=upstream_change_oid or None,
    )
    ms = round((time.monotonic() - t0) * 1000, 1)
    value = raw.get("value") if isinstance(raw, dict) else None
    if not isinstance(value, list):
        value = []
    if session:
        log_session_event(
            session, "INFO", "transformer:detect", 0, ms, "service",
            f"target={target_path} sources={len(source_part_paths or [])} "
            f"discrepancies={len(value)}",
        )
    return TransformResponse(
        ok=True,
        action="DetectDiscrepancies",
        value=value,
        raw=raw if isinstance(raw, dict) else {},
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def generate_downstream(
    client: WRSClient,
    target_path: str,
    source_part_paths: list[str],
    upstream_change_oid: str = "",
    change_oid: str = "",
    session: Optional[UserSession] = None,
) -> TransformResponse:
    """Wrapper around ``client.generate_downstream_structure``."""
    t0 = time.monotonic()
    raw = client.generate_downstream_structure(
        target_path=target_path,
        source_part_paths=source_part_paths,
        upstream_change_oid=upstream_change_oid or None,
        change_oid=change_oid or None,
    )
    ms = round((time.monotonic() - t0) * 1000, 1)
    value = raw.get("value") if isinstance(raw, dict) else None
    if not isinstance(value, list):
        value = []
    if session:
        log_session_event(
            session, "INFO", "transformer:generate", 0, ms, "service",
            f"target={target_path} sources={len(source_part_paths)} "
            f"created={len(value)} changeOid={change_oid or '-'}",
        )
    return TransformResponse(
        ok=True,
        action="GenerateDownstreamStructure",
        value=value,
        raw=raw if isinstance(raw, dict) else {},
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


def paste_special(
    client: WRSClient,
    target_path: str,
    source_part_paths: list[str],
    upstream_change_oid: str = "",
    change_oid: str = "",
    session: Optional[UserSession] = None,
) -> TransformResponse:
    """Wrapper around ``client.paste_special`` (per-node COPY)."""
    t0 = time.monotonic()
    raw = client.paste_special(
        target_path=target_path,
        source_part_paths=source_part_paths,
        upstream_change_oid=upstream_change_oid or None,
        change_oid=change_oid or None,
    )
    ms = round((time.monotonic() - t0) * 1000, 1)
    value = raw.get("value") if isinstance(raw, dict) else None
    if not isinstance(value, list):
        value = []
    if session:
        log_session_event(
            session, "INFO", "transformer:copy", 0, ms, "service",
            f"target={target_path} sources={len(source_part_paths)} "
            f"copied={len(value)} changeOid={change_oid or '-'}",
        )
    return TransformResponse(
        ok=True,
        action="PasteSpecial",
        value=value,
        raw=raw if isinstance(raw, dict) else {},
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )


# ── Phase 2c — REMOVE (delete UsageLinks via PTC.ProdMgmt) ──


def remove_usage_links(
    client: WRSClient,
    usage_link_ids: list[str],
    session: Optional[UserSession] = None,
) -> TransformRemoveResponse:
    """Delete a list of WTPartUsageLinks (per-node REMOVE on the MBOM side).

    Loops over IDs, calls ``client.remove_bom_child`` for each, and reports
    per-link success/failure. Does **not** abort on first error — collects
    all results so the UI can show partial progress.
    """
    t0 = time.monotonic()
    removed: list[str] = []
    failed: list[dict[str, str]] = []

    for link_id in usage_link_ids:
        if not link_id:
            failed.append({"usageLinkId": "", "error": "empty id"})
            continue
        try:
            client.remove_bom_child(link_id)
            removed.append(link_id)
        except Exception as exc:  # noqa: BLE001 — collect & continue
            failed.append({"usageLinkId": link_id, "error": str(exc)})
            logger.warning("transformer:remove failed for %s: %s", link_id, exc)

    ms = round((time.monotonic() - t0) * 1000, 1)
    if session:
        log_session_event(
            session, "INFO", "transformer:remove", 0, ms, "service",
            f"requested={len(usage_link_ids)} removed={len(removed)} failed={len(failed)}",
        )
    return TransformRemoveResponse(
        ok=len(failed) == 0,
        removed=removed,
        failed=failed,
        timing=TimingInfo(totalMs=ms, wrsMs=ms),
    )
