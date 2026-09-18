"""Read-only export cleaning report inspection tool."""

from __future__ import annotations

from typing import Any

from ..models import ToolResult


def inspect_export_cleaning(client: Any, limit: int | None = None) -> ToolResult:
    exports = client.list_exports(limit=limit)
    degraded = []
    summaries = []
    for item in exports:
        cleaning = item.get("cleaning") or {}
        degraded_messages = cleaning.get("degraded") or []
        if degraded_messages:
            degraded.append(item.get("id"))
        summaries.append(
            {
                "id": item.get("id"),
                "status": item.get("status"),
                "row_count": item.get("row_count"),
                "mode": cleaning.get("mode") or (item.get("params") or {}).get("clean_mode"),
                "pages_cleaned": cleaning.get("pages_cleaned"),
                "characters_before": cleaning.get("characters_before"),
                "characters_after": cleaning.get("characters_after"),
                "reverted_pages": cleaning.get("reverted_pages"),
                "degraded": bool(degraded_messages),
            }
        )
    warnings = ["CLEAN_MODE_DEGRADED"] if degraded else []
    return ToolResult(
        tool_name="inspect_export_cleaning",
        answer=f"Inspected {len(exports)} export records.",
        evidence=[{"field": "cleaning_summaries", "observed": summaries}],
        metrics={"export_count": len(exports), "degraded_export_count": len(degraded), "exports": summaries},
        warnings=warnings,
    )
