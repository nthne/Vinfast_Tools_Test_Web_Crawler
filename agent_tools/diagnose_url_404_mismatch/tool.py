"""Compare a crawler URL with the current upstream document URL."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx

from crawler_client.schemas import CrawledPage

from ..models import ToolResult


Probe = Callable[[str, float], dict[str, Any]]


def _safe_url(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}" if parsed.netloc else parsed.path


def _path_key(url: str) -> tuple[str, str]:
    parsed = urlsplit(url)
    path = parsed.path.rstrip("/") or "/"
    return parsed.netloc.casefold(), path.casefold()


def _same_document(url: str, expected_url: str) -> bool:
    current = urlsplit(url)
    expected = urlsplit(expected_url)
    if current.netloc.casefold() != expected.netloc.casefold():
        return False
    current_name = current.path.rstrip("/").rsplit("/", 1)[-1].casefold()
    expected_name = expected.path.rstrip("/").rsplit("/", 1)[-1].casefold()
    return bool(current_name and expected_name and current_name == expected_name)


def _default_probe(url: str, timeout: float) -> dict[str, Any]:
    response = httpx.get(
        url,
        follow_redirects=True,
        timeout=timeout,
        headers={"User-Agent": "web-crawl-qa/1.0 url-404-diagnostic"},
    )
    return {
        "status_code": response.status_code,
        "final_url": str(response.url),
        "content_type": response.headers.get("content-type"),
    }


def _probe(probe_url: Probe, url: str, timeout: float) -> dict[str, Any]:
    try:
        observed = probe_url(url, timeout)
        return dict(observed)
    except Exception as exc:  # A probe failure is evidence, not a scan-wide failure.
        return {"status_code": None, "error": f"{exc.__class__.__name__}: {exc}"}


def _candidate_pages(pages: list[CrawledPage], expected_url: str) -> list[CrawledPage]:
    matching = [page for page in pages if _same_document(page.url, expected_url)]
    if matching:
        return matching
    return [page for page in pages if page.status_code == 404]


def _source_url_diagnostics(client: Any, job_id: str, pages: list[CrawledPage], expected_url: str) -> dict[str, Any]:
    """Detect file-like source URLs that misresolve relative links."""

    get_job = getattr(client, "get_job", None)
    get_source = getattr(client, "get_source", None)
    if get_job is None or get_source is None:
        return {}
    try:
        job = get_job(job_id)
        source_id = str(job.get("source_id") or "")
        source = get_source(source_id) if source_id else {}
        source_url = str(source.get("url") or "")
    except Exception:
        return {}
    if not source_url:
        return {}

    relative_name = urlsplit(expected_url).path.rstrip("/").rsplit("/", 1)[-1]
    without_slash = urljoin(source_url, relative_name)
    with_slash = urljoin(source_url.rstrip("/") + "/", relative_name)
    crawler_urls = {page.url for page in pages}
    missing_slash_root_cause = (
        not urlsplit(source_url).path.endswith("/")
        and without_slash in crawler_urls
        and with_slash != without_slash
    )
    return {
        "source_url": _safe_url(source_url),
        "source_url_has_trailing_slash": urlsplit(source_url).path.endswith("/"),
        "relative_resolution_without_slash": _safe_url(without_slash),
        "relative_resolution_with_slash": _safe_url(with_slash),
        "relative_link_root_cause": (
            "SOURCE_URL_MISSING_TRAILING_SLASH" if missing_slash_root_cause else None
        ),
    }


def diagnose_url_404_mismatch(
    client: Any,
    job_id: str,
    expected_url: str,
    sample_pages: int | None = None,
    max_probes: int = 20,
    request_timeout: float = 15.0,
    probe_url: Probe | None = None,
) -> ToolResult:
    """Check whether a crawler 404 is caused by a stale/versioned URL path."""

    pages = client.list_pages(job_id=job_id, limit=sample_pages)
    probe = probe_url or _default_probe
    expected_probe = _probe(probe, expected_url, request_timeout)
    candidates = _candidate_pages(pages, expected_url)
    source_diagnostics = _source_url_diagnostics(client, job_id, pages, expected_url)
    candidate_observations: list[dict[str, Any]] = []
    for page in candidates[: max(0, max_probes)]:
        upstream = _probe(probe, page.url, request_timeout)
        crawler_status = page.status_code
        candidate_observations.append(
            {
                "page_id": page.page_id,
                "crawler_url": _safe_url(page.url),
                "crawler_status_code": crawler_status,
                "upstream_status_code": upstream.get("status_code"),
                "upstream_final_url": _safe_url(str(upstream.get("final_url") or "")),
                "upstream_content_type": upstream.get("content_type"),
                "probe_error": upstream.get("error"),
            }
        )

    expected_status = expected_probe.get("status_code")
    mismatch = [
        item
        for item in candidate_observations
        if expected_status is not None
        and 200 <= int(expected_status) < 400
        and (
            item.get("crawler_status_code") == 404
            or item.get("upstream_status_code") == 404
        )
    ]
    if expected_status is not None and 200 <= int(expected_status) < 400 and mismatch:
        classification = "CRAWLER_URL_VERSION_MISMATCH"
        answer = (
            f"The current document URL returns HTTP {expected_status}, but the crawler has "
            f"{len(mismatch)} matching candidate URL(s) that resolve to 404."
        )
        if source_diagnostics.get("relative_link_root_cause"):
            answer += (
                " The source URL is missing a trailing slash, so a relative document link "
                "can resolve against the wrong directory."
            )
    elif expected_status == 404:
        classification = "UPSTREAM_404_CONFIRMED"
        answer = "The expected URL itself currently returns HTTP 404."
    elif not candidate_observations:
        classification = "NO_MATCHING_CRAWLER_PAGE"
        answer = "No crawler page matched the expected document name/path heuristic."
    else:
        classification = "NO_404_MISMATCH_OBSERVED"
        answer = "The probe did not reproduce a current-URL success versus crawler-URL 404 mismatch."

    warnings = ["READ_ONLY_UPSTREAM_PROBE", "URL_QUERY_AND_FRAGMENT_OMITTED_FROM_EVIDENCE"]
    if source_diagnostics.get("relative_link_root_cause"):
        warnings.append("SOURCE_URL_MISSING_TRAILING_SLASH")
    return ToolResult(
        tool_name="diagnose_url_404_mismatch",
        answer=answer,
        evidence=candidate_observations,
        metrics={
            "job_id": job_id,
            "expected_url": _safe_url(expected_url),
            "expected_status_code": expected_status,
            "crawler_page_count": len(pages),
            "candidate_count": len(candidates),
            "probed_candidate_count": len(candidate_observations),
            "crawler_404_count": sum(item.get("crawler_status_code") == 404 for item in candidate_observations),
            "upstream_404_count": sum(item.get("upstream_status_code") == 404 for item in candidate_observations),
            "mismatch_count": len(mismatch),
            "expected_final_url": _safe_url(str(expected_probe.get("final_url") or "")),
            "expected_content_type": expected_probe.get("content_type"),
            **source_diagnostics,
        },
        warnings=warnings,
        recommended_actions=[
            "Verify the source seed URL and link extraction rule that produced the crawler path.",
            "Check whether the crawler follows the current versioned documentation links.",
            "Re-run one page after correcting the seed/path rule before starting a full crawl.",
        ],
        classification=classification,
    )
