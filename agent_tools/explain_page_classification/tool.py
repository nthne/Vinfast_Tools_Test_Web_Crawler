"""Explain crawler kind independently from response MIME."""

from __future__ import annotations

from typing import Any

from crawler_client.schemas import CrawledPage

from ..models import ToolResult


def explain_page_classification(client: Any, page_id: str) -> ToolResult:
    page = client.get_page(page_id)
    metadata = page.metadata if isinstance(page.metadata, dict) else {}
    kind = str(metadata.get("kind") or "UNKNOWN")
    content_type = str(page.content_type or "UNKNOWN").lower()
    warnings = list(metadata.get("warnings") or [])
    signals: list[str] = []
    if kind == "RESOURCE" and content_type == "text/html":
        signals.append("RESOURCE_URL_RETURNS_HTML")
    if kind == "RESOURCE" and any("redirected_to" in str(item) for item in warnings):
        signals.append("REDIRECT_RESOURCE_TO_HTML")
    if kind == "NAVIGATION" and content_type.startswith("image/"):
        signals.append("NAVIGATION_URL_RETURNS_BINARY")
    if not metadata.get("discovery_context"):
        signals.append("DISCOVERY_CONTEXT_UNAVAILABLE")
    return ToolResult(
        tool_name="explain_page_classification",
        answer=f"The crawler classified this record as {kind}; response MIME is {content_type}.",
        evidence=[
            {"field": "kind", "observed": kind},
            {"field": "content_type", "observed": content_type},
            {"field": "content_route", "observed": metadata.get("content_route")},
            {"field": "warnings", "observed": warnings},
        ],
        metrics={
            "page_id": page_id,
            "kind": kind,
            "content_type": content_type,
            "content_route": metadata.get("content_route"),
            "signals": signals,
            "discovery_context": metadata.get("discovery_context"),
        },
        warnings=signals,
        confidence="observed",
    )
