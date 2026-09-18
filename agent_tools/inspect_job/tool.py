"""Read-only job status and counter inspection tool."""

from __future__ import annotations

from typing import Any

from ..models import ToolResult


def inspect_job(client: Any, job_id: str, sample_pages: int = 0) -> ToolResult:
    job = client.get_job(job_id)
    config = job.get("crawl_config") or {}
    metadata = job.get("metadata") or {}
    max_pages = config.get("max_pages")
    max_resources = config.get("max_resources")
    effective_budget = None
    if isinstance(max_pages, int) and isinstance(max_resources, int):
        effective_budget = max_pages + max_resources
    sample_count = 0
    if sample_pages:
        sample_count = len(client.list_pages(job_id=job_id, limit=sample_pages))
    return ToolResult(
        tool_name="inspect_job",
        answer=f"Job {job_id} is {job.get('status') or 'unknown'}.",
        evidence=[
            {"field": "status", "observed": job.get("status")},
            {"field": "runtime_crawl_config", "observed": dict(config)},
            {"field": "metadata", "observed": dict(metadata)},
        ],
        metrics={
            "job_id": job.get("id") or job_id,
            "source_id": job.get("source_id"),
            "status": job.get("status"),
            "started_at": job.get("started_at"),
            "updated_at": job.get("updated_at"),
            "finished_at": job.get("finished_at"),
            "max_pages": max_pages,
            "max_resources": max_resources,
            "effective_record_budget": effective_budget,
            "total_pages": metadata.get("total_pages"),
            "in_queue_count": metadata.get("in_queue_count"),
            "success_count": metadata.get("success_count"),
            "failed_count": metadata.get("failed_count"),
            "skipped_count": metadata.get("skipped_count"),
            "sample_page_count": sample_count,
        },
        warnings=list(metadata.get("error_summary") or []),
    )
