"""Explain clean output length changes with observed preview metrics."""

from __future__ import annotations

from typing import Any

from ..compare_clean_modes.tool import _preview_metrics
from ..models import ToolResult


def explain_clean_output_length(client: Any, page_id: str, mode: str = "SAFE") -> ToolResult:
    preview = client.preview_clean(page_id, mode, scope="PAGE")
    metrics = _preview_metrics(preview)
    warnings: list[str] = []
    ratio = metrics["retention_ratio"]
    if isinstance(ratio, (int, float)) and ratio > 1:
        warnings.append("CLEAN_OUTPUT_EXPANDED")
    if isinstance(ratio, (int, float)) and ratio < 0.10:
        warnings.append("CLEANING_OVER_AGGRESSIVE")
    if metrics["original_characters"] and metrics["kept_characters"] == 0:
        warnings.append("CLEAN_RESULT_EMPTY")
    if metrics["degraded"]:
        warnings.append("CLEAN_MODE_DEGRADED")
    return ToolResult(
        tool_name="explain_clean_output_length",
        answer=f"{mode} kept {metrics['kept_characters']} of {metrics['original_characters']} characters.",
        evidence=[
            {"field": "original_characters", "observed": metrics["original_characters"]},
            {"field": "kept_characters", "observed": metrics["kept_characters"]},
            {"field": "retention_ratio", "observed": metrics["retention_ratio"]},
            {"field": "degraded", "observed": metrics["degraded_messages"]},
        ],
        metrics={"page_id": page_id, "mode": mode, **metrics},
        warnings=sorted(set(warnings)),
    )
