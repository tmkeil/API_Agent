"""
WRS Client — Where-Used / Einsatzverwendung (Mixin).
=====================================================

In welchen Parent-Baugruppen ist ein Part verbaut?
Wird in ``WRSClient`` per Mehrfachvererbung eingebunden.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.core.odata import extract_id

if TYPE_CHECKING:
    from src.adapters.base import WRSClientBase

logger = logging.getLogger(__name__)


class WhereUsedMixin:
    """Einsatzverwendung (Where-Used) — Mixin fuer WRSClientBase."""

    def get_where_used(self: "WRSClientBase", part_id: str) -> list[dict]:
        """Einsatzverwendung (Where-Used): in welchen Parent-Parts ist dieses Teil verbaut?

        Versucht mehrere OData-Pfade:
          1. PTC.ProdMgmt.GetWhereUsed Action (Windchill 12+)
          2. UsedBy Navigation Property
          3. UsageLinks mit $expand auf Uses (Reverse-Lookup)

        Returns:
            Liste von dicts mit Parent-Part-Informationen.
        """
        results: list[dict] = []
        seen: set[str] = set()

        # Strategie 1: GetWhereUsed Action
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/PTC.ProdMgmt.GetWhereUsed"
        resp = self._get(url, suppress_errors=True)
        if resp and resp.status_code == 200:
            data = resp.json()
            items = data.get("value", [])
            if isinstance(items, list):
                for item in items:
                    pid = extract_id(item)
                    if pid and pid not in seen:
                        seen.add(pid)
                        results.append(item)
            if results:
                return results

        # Strategie 2: UsedBy Navigation Property
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/UsedBy"
        items = self._get_all_pages(url, return_none_on_error=True)
        if items:
            for link in items:
                # UsedBy links point to the parent; try to resolve
                parent = link.get("Uses") or link.get("UsedBy") or link
                pid = extract_id(parent)
                if pid and pid not in seen:
                    seen.add(pid)
                    # If it's a link, try expanding to get the parent part
                    parent_data = self.get_part_by_id(pid) if not parent.get("Number") else parent
                    if parent_data:
                        results.append(parent_data)
            if results:
                return results

        # Strategie 3: UsageLinks mit $filter auf Uses Part
        url = f"{self.odata_base}/ProdMgmt/Parts('{part_id}')/UsageLinks"
        items = self._get_all_pages(url, {"$expand": "Uses"}, return_none_on_error=True)
        if items:
            for link in items:
                parent = link.get("Uses") or {}
                pid = extract_id(parent)
                if pid and pid not in seen:
                    seen.add(pid)
                    results.append(parent)

        return results
