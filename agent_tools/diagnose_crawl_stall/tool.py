"""Bounded, read-only diagnostics for long-running crawl jobs."""

from __future__ import annotations

import time
from collections import Counter
from typing import Any
from urllib.parse import urlsplit

from ..models import ToolResult


def _url_route(url: str) -> tuple[str, str, str]:
    parsed = urlsplit(url)
    return parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/") or "/"


def _snapshot(job: dict[str, Any]) -> tuple[Any, ...]:
    metadata = job.get("metadata") or {}
    return (
        job.get("status"),
        job.get("updated_at"),
        metadata.get("total_pages"),
        metadata.get("in_queue_count"),
        metadata.get("success_count"),
        metadata.get("failed_count"),
        metadata.get("skipped_count"),
    )


def diagnose_crawl_stall(
    client: Any,
    job_id: str,
    poll_seconds: int = 0,
    sample_pages: tuple[int, ...] = (1, 2, 10),
) -> ToolResult:
    job = client.get_job(job_id)
    runtime_config = job.get("crawl_config") or {}
    metadata = job.get("metadata") or {}
    source = client.get_source(str(job.get("source_id"))) if job.get("source_id") else {}
    source_config = source.get("crawl_config") or {}
    max_pages = runtime_config.get("max_pages")
    max_resources = runtime_config.get("max_resources")
    effective_budget = max_pages + max_resources if isinstance(max_pages, int) and isinstance(max_resources, int) else None
    source_resource_budget = source_config.get("max_resources")
    resource_delta = None
    if isinstance(max_resources, int) and isinstance(source_resource_budget, int):
        resource_delta = max_resources - source_resource_budget

    sample_limit = max(1, max(sample_pages, default=1)) * 100
    pages = client.list_pages(job_id=job_id, limit=sample_limit)
    urls = [str(page.url) for page in pages if page.url]
    exact_urls = Counter(urls)
    routes = Counter(_url_route(url) for url in urls)
    expansion_pages = []
    for page in pages:
        url = str(page.url)
        segments = [segment for segment in urlsplit(url).path.split("/") if segment]
        segment_counts = Counter(segments)
        if len(url) > 1000 or any(count >= 3 for count in segment_counts.values()):
            expansion_pages.append(page)

    warnings: list[str] = []
    if resource_delta not in (None, 0):
        warnings.append("JOB_RUNTIME_CONFIG_DIFFERS_FROM_SOURCE")
    if effective_budget is not None and metadata.get("total_pages", 0) >= effective_budget and metadata.get("in_queue_count", 0) > 0:
        warnings.append("JOB_BUDGET_EXHAUSTED_NOT_TERMINATED")
    if expansion_pages:
        warnings.append("URL_PATH_EXPANSION")
    if any(count > 1 for count in exact_urls.values()):
        warnings.append("EXACT_DUPLICATE_URL")
    if any(count > 1 for count in routes.values()):
        warnings.append("URL_ROUTE_VARIANTS")

    stalled = False
    poll_evidence: dict[str, Any] = {"performed": False}
    if poll_seconds > 0:
        bounded_seconds = min(int(poll_seconds), 60)
        time.sleep(bounded_seconds)
        later_job = client.get_job(job_id)
        stalled = _snapshot(job) == _snapshot(later_job)
        poll_evidence = {"performed": True, "seconds": bounded_seconds, "stalled": stalled, "before": _snapshot(job), "after": _snapshot(later_job)}
        if stalled:
            warnings.append("JOB_STALLED")

    if stalled:
        classification = "STALLED"
    elif expansion_pages:
        classification = "URL_EXPANSION_SUSPECTED"
    elif effective_budget is not None and metadata.get("total_pages", 0) >= effective_budget and metadata.get("in_queue_count", 0) > 0:
        classification = "BUDGET_EXHAUSTED"
    elif job.get("status") == "RUNNING":
        classification = "PROGRESSING"
    else:
        classification = "UNKNOWN"

    return ToolResult(
        tool_name="diagnose_crawl_stall",
        answer=f"Job {job_id} classified as {classification} from bounded read-only checks.",
        evidence=[
            {"field": "runtime_crawl_config", "observed": runtime_config},
            {"field": "source_crawl_config", "observed": source_config},
            {"field": "job_metadata", "observed": metadata},
            {"field": "poll", "observed": poll_evidence},
        ],
        metrics={
            "job_id": job_id,
            "classification": classification,
            "status": job.get("status"),
            "effective_record_budget": effective_budget,
            "total_pages": metadata.get("total_pages"),
            "in_queue_count": metadata.get("in_queue_count"),
            "runtime_source_resource_budget_delta": resource_delta,
            "sample_count": len(pages),
            "exact_duplicate_url_groups": sum(1 for count in exact_urls.values() if count > 1),
            "same_route_variant_groups": sum(1 for count in routes.values() if count > 1),
            "url_path_expansion_count": len(expansion_pages),
            "max_url_length": max((len(url) for url in urls), default=0),
            "poll_performed": poll_evidence["performed"],
            "poll_stalled": stalled,
        },
        warnings=sorted(set(warnings)),
        classification=classification,
        recommended_actions=[
            "Compare the persisted job crawl_config with the intended source configuration.",
            "Inspect URL canonicalization and external resource allowlists before starting another full crawl.",
        ],
    )
