"""BOM Transformation write operations — Phase 2 (skeleton).

This mixin will host bulk-write operations such as
`generate_downstream_structure` (clone Design BOM → Manufacturing BOM and
wire BALDOWNSTREAM equivalence links).

Implementation note (verified on plm-prod, OData v6):
  - PTC v3/BomTransformation domain is NOT deployed.
  - BAL_DOWNSTREAMNav is NOT exposed on Parts.
Therefore the bulk operation must be orchestrated client-side via the
existing per-node primitives:
  - adapters/write_mixin.add_bom_child / remove_bom_child
  - services/write_service.add_downstream_link / remove_downstream_link

Phase 1 (current) is read-only; this file intentionally contains only
stubs raising NotImplementedError so the import surface is stable.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.adapters.wrs_client import WRSClientBase  # noqa: F401


def generate_downstream_structure(
    self: "WRSClientBase",
    design_part_code: str,
    *,
    target_org: str | None = None,
    target_view: str = "Manufacturing",
    suffix: str = "-M",
) -> dict[str, Any]:
    """Generate (or refresh) the Manufacturing-side equivalent of a Design BOM.

    Phase 2 — not yet implemented.

    Planned contract (subject to change):
      In:  design_part_code, optional target_org, target_view, number suffix.
      Out: { "rootNumber": str, "createdParts": [...], "createdLinks": [...],
             "skipped": [...], "errors": [...] }
    """
    raise NotImplementedError(
        "generate_downstream_structure is a Phase 2 feature and is not yet "
        "implemented. Use add_bom_child / add_downstream_link per node for now."
    )
