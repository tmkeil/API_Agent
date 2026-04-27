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
