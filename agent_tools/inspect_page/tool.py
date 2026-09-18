"""Read-only page metadata inspection tool."""

from __future__ import annotations

from typing import Any

from crawler_client.schemas import CrawledPage

from ..models import ToolResult


def _metadata(page: CrawledPage) -> dict[str, Any]:
    return page.metadata if isinstance(page.metadata, dict) else {}


def inspect_page(client: Any, page_id: str) -> ToolResult:
    page = client.get_page(page_id)
    metadata = _metadata(page)
    return ToolResult(
        tool_name="inspect_page",
        answer=f"Page {page_id} was inspected; content is summarized without returning the body.",
        evidence=[
            {"field": "kind", "observed": metadata.get("kind")},
            {"field": "content_type", "observed": page.content_type},
            {"field": "content_route", "observed": metadata.get("content_route")},
            {"field": "warnings", "observed": metadata.get("warnings") or []},
        ],
        metrics={
            "page_id": page.page_id,
            "source_id": page.source_id,
            "job_id": page.job_id,
            "url": page.url,
            "final_url": page.final_url or metadata.get("final_url"),
            "kind": metadata.get("kind"),
            "status": metadata.get("status"),
            "status_code": page.status_code or metadata.get("status_code"),
            "content_type": page.content_type,
            "content_route": metadata.get("content_route"),
            "title_present": bool(page.title or metadata.get("title")),
            "markdown_characters": len(page.markdown or ""),
            "extracted_characters": len(page.extracted_text or ""),
            "clean_characters": len(page.clean_text or ""),
            "word_count": page.word_count,
            "depth": metadata.get("depth"),
            "links_count": len(metadata.get("links") or []) if isinstance(metadata.get("links"), list) else None,
        },
        warnings=list(metadata.get("warnings") or []),
    )
