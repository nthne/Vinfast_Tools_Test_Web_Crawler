"""Compare page view and RAW clean-preview provenance."""

from __future__ import annotations

from typing import Any

from ..compare_clean_modes.tool import _preview_metrics
from ..models import ToolResult


def check_raw_provenance(client: Any, page_id: str) -> ToolResult:
    page_view = client.get_page_view(page_id)
    raw_preview = client.preview_clean(page_id, "RAW", scope="PAGE")
    page_view_characters = len(str(page_view.get("markdown") or ""))
    raw_metrics = _preview_metrics(raw_preview)
    warnings: list[str] = []
    if raw_metrics["matches_export"] is False:
        warnings.append("CLEAN_PREVIEW_EXPORT_MISMATCH")
    if isinstance(raw_metrics["original_characters"], (int, float)) and page_view_characters != raw_metrics["original_characters"]:
        warnings.append("CLEAN_PREVIEW_INPUT_MISMATCH")
    return ToolResult(
        tool_name="check_raw_provenance",
        answer="Compared page view markdown with the RAW clean-preview input without returning content.",
        evidence=[
            {"field": "page_view_characters", "observed": page_view_characters},
            {"field": "clean_preview_raw", "observed": raw_metrics},
        ],
        metrics={
            "page_id": page_id,
            "page_view_characters": page_view_characters,
            "clean_preview_raw_characters": raw_metrics["original_characters"],
            "raw_kept_characters": raw_metrics["kept_characters"],
            "matches_export": raw_metrics["matches_export"],
        },
        warnings=sorted(set(warnings)),
    )
