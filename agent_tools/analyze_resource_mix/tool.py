"""Read-only navigation/resource distribution analysis tool."""

from __future__ import annotations

from collections import Counter
from typing import Any
from urllib.parse import urlsplit

from crawler_client.schemas import CrawledPage

from ..models import ToolResult


def _metadata(page: CrawledPage) -> dict[str, Any]:
    return page.metadata if isinstance(page.metadata, dict) else {}


def _host(url: str | None) -> str:
    return urlsplit(str(url or "")).netloc.lower()


def analyze_resource_mix(client: Any, job_id: str, sample_pages: int = 8, page_size: int = 100) -> ToolResult:
    limit = max(1, sample_pages * page_size) if sample_pages else None
    pages = client.list_pages(job_id=job_id, limit=limit)
    resource_pages = [page for page in pages if _metadata(page).get("kind") == "RESOURCE"]
    navigation_hosts = {_host(page.url) for page in pages if _metadata(page).get("kind") == "NAVIGATION"}
    content_types = Counter((page.content_type or "UNKNOWN").lower() for page in resource_pages)
    routes = Counter(str(_metadata(page).get("content_route") or "UNKNOWN") for page in resource_pages)
    external = [page for page in resource_pages if _host(page.url) not in navigation_hosts]
    html_resources = [page for page in resource_pages if (page.content_type or "").lower() == "text/html"]
    image_resources = [page for page in resource_pages if (page.content_type or "").lower().startswith("image/")]
    repeated_path_pages = [
        page for page in resource_pages if str(page.url).count("/static/") >= 3 or len(str(page.url)) > 1000
    ]
    warnings: list[str] = []
    if html_resources:
        warnings.append("RESOURCE_URL_RETURNS_HTML")
    if external:
        warnings.append("EXTERNAL_RESOURCE_OVER_COLLECTION")
    if repeated_path_pages:
        warnings.append("URL_PATH_EXPANSION")
    return ToolResult(
        tool_name="analyze_resource_mix",
        answer=f"Analyzed {len(pages)} sampled records for job {job_id}; {len(resource_pages)} are resources.",
        evidence=[
            {"field": "resource_count", "observed": len(resource_pages)},
            {"field": "content_type_distribution", "observed": dict(content_types)},
            {"field": "content_route_distribution", "observed": dict(routes)},
            {"field": "external_resource_count", "observed": len(external)},
        ],
        metrics={
            "job_id": job_id,
            "sample_count": len(pages),
            "resource_count": len(resource_pages),
            "navigation_count": len(pages) - len(resource_pages),
            "image_count": len(image_resources),
            "html_resource_count": len(html_resources),
            "external_resource_count": len(external),
            "repeated_path_or_long_url_count": len(repeated_path_pages),
            "content_types": dict(content_types),
            "content_routes": dict(routes),
        },
        warnings=warnings,
    )
