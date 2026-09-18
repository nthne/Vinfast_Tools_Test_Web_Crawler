"""Read-only comparison of crawler cleaning modes."""

from __future__ import annotations

from typing import Any

from ..models import ToolResult


def _preview_metrics(preview: dict[str, Any]) -> dict[str, Any]:
    original = preview.get("original_characters")
    kept = preview.get("kept_characters")
    ratio = None
    if isinstance(original, (int, float)) and original:
        ratio = kept / original if isinstance(kept, (int, float)) else None
    return {
        "scope": preview.get("scope"),
        "matches_export": preview.get("matches_export"),
        "original_characters": original,
        "kept_characters": kept,
        "retention_ratio": ratio,
        "reverted": preview.get("reverted"),
        "degraded": bool(preview.get("degraded")),
        "degraded_messages": preview.get("degraded") or [],
    }


def compare_clean_modes(client: Any, page_id: str, modes: list[str] | None = None) -> ToolResult:
    catalog = client.list_clean_modes()
    if modes is None:
        modes = [str(item.get("mode")) for item in catalog.get("items", []) if item.get("mode")]
    results: dict[str, dict[str, Any]] = {}
    warnings: list[str] = []
    for mode in modes:
        preview = client.preview_clean(page_id, mode, scope="PAGE")
        results[mode] = _preview_metrics(preview)
        if results[mode]["degraded"]:
            warnings.append("CLEAN_MODE_DEGRADED")
        if results[mode]["reverted"]:
            warnings.append("CLEAN_REVERTED_PAGE")
    return ToolResult(
        tool_name="compare_clean_modes",
        answer=f"Compared {len(results)} clean modes for page {page_id}.",
        evidence=[
            {"field": "clean_mode_catalog", "observed": [item.get("mode") for item in catalog.get("items", [])]},
            {"field": "llm_ready", "observed": catalog.get("llm_ready")},
            {"field": "previews", "observed": results},
        ],
        metrics={"page_id": page_id, "llm_ready": catalog.get("llm_ready"), "modes": results},
        warnings=sorted(set(warnings)),
    )
