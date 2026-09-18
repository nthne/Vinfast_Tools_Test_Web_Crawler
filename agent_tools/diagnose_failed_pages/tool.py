"""Read-only diagnostics for systematic page failures."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

from crawler_client.schemas import CrawledPage

from ..models import ToolResult


def _metadata(page: CrawledPage) -> dict[str, Any]:
    return page.metadata if isinstance(page.metadata, dict) else {}


def _failure_payload(page: CrawledPage) -> Mapping[str, Any]:
    metadata = _metadata(page)
    failure = metadata.get("failure")
    if isinstance(failure, Mapping):
        return failure
    error = metadata.get("error")
    return error if isinstance(error, Mapping) else {}


def _error_code(page: CrawledPage) -> str:
    metadata = _metadata(page)
    payload = _failure_payload(page)
    code = payload.get("code")
    if not code and isinstance(metadata.get("error"), Mapping):
        code = metadata["error"].get("code")
    return str(code or "UNKNOWN_ERROR")


def _error_message(page: CrawledPage) -> str:
    metadata = _metadata(page)
    payload = _failure_payload(page)
    message = payload.get("detail") or payload.get("message")
    if message:
        return str(message)
    error = metadata.get("error")
    if isinstance(error, Mapping):
        return str(error.get("detail") or error.get("message") or "")
    return ""


def _safe_url(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}" if parsed.netloc else parsed.path


def diagnose_failed_pages(client: Any, job_id: str, sample_pages: int | None = None) -> ToolResult:
    """Explain whether page failures are HTTP/site failures or crawler infrastructure failures."""

    job = client.get_job(job_id)
    pages = client.list_pages(job_id=job_id, limit=sample_pages)
    failed = [page for page in pages if str(_metadata(page).get("status") or "").upper() == "FAILED"]
    navigation = [page for page in pages if str(_metadata(page).get("kind") or "").upper() == "NAVIGATION"]
    failed_navigation = [page for page in failed if str(_metadata(page).get("kind") or "").upper() == "NAVIGATION"]
    failed_resources = [page for page in failed if str(_metadata(page).get("kind") or "").upper() == "RESOURCE"]

    error_codes = Counter(_error_code(page) for page in failed)
    error_signatures = Counter(f"{_error_code(page)}: {_error_message(page)}".strip() for page in failed)
    renderer_failures = [
        page for page in failed
        if any(marker in _error_message(page).casefold() for marker in ("js_escalation_failed", "cdp", "renderer error"))
    ]
    no_http_response = [page for page in failed if page.status_code is None]
    non_retryable = [page for page in failed if _failure_payload(page).get("retryable") is False]
    http_failures = [page for page in failed if page.status_code is not None]
    job_metadata = job.get("metadata") or {}
    job_config = job.get("crawl_config") or {}
    total_observed = len(pages)
    failure_rate = len(failed) / total_observed if total_observed else 0.0
    renderer_rate = len(renderer_failures) / len(failed) if failed else 0.0

    if not failed:
        classification = "NO_FAILURES"
    elif renderer_rate >= 0.8:
        classification = "RENDERER_INFRASTRUCTURE_FAILURE"
    elif http_failures and len(http_failures) == len(failed):
        classification = "HTTP_FAILURE"
    elif len(failed) == total_observed:
        classification = "SYSTEMIC_FAILURE"
    else:
        classification = "MIXED_FAILURE"

    warnings: list[str] = []
    if renderer_failures:
        warnings.append("JS_ESCALATION_FAILURE")
    if no_http_response:
        warnings.append("NO_HTTP_RESPONSE_RECORDED")
    if non_retryable and len(non_retryable) == len(failed):
        warnings.append("CRW_PERMANENT_NOT_RETRIED")
    if failed_navigation and len(failed_navigation) / len(navigation or [1]) >= 0.8:
        warnings.append("NAVIGATION_FAILURE_DOMINATES")
    if str(job.get("status") or "").upper() == "COMPLETED" and failure_rate >= 0.5:
        warnings.append("JOB_COMPLETED_WITH_SYSTEMIC_FAILURE")

    actions: list[str] = []
    if renderer_failures:
        actions.extend(
            [
                "Kiểm tra log và health của browser/renderer worker tại thời điểm job chạy.",
                "Chạy thử một URL với render_js=false hoặc HTTP-only nếu nội dung không cần JavaScript.",
                "Nếu bắt buộc render JavaScript, sửa lỗi CDP/session trước khi crawl lại.",
            ]
        )
    if no_http_response:
        actions.append("Không kết luận site trả 4xx/5xx; lỗi xảy ra trước khi crawler ghi nhận HTTP response.")
    if not actions:
        actions.append("Kiểm tra failure detail và retry policy của nhóm page trước khi retry có kiểm soát.")

    samples = [
        {
            "page_id": page.page_id,
            "url": _safe_url(page.url),
            "kind": _metadata(page).get("kind"),
            "status_code": page.status_code,
            "error_code": _error_code(page),
            "error_message": _error_message(page),
        }
        for page in failed[:5]
    ]
    return ToolResult(
        tool_name="diagnose_failed_pages",
        answer=f"Job {job_id} có {len(failed)}/{total_observed} page failed; mẫu lỗi chính được phân loại là {classification}.",
        evidence=[
            {"field": "job_config", "observed": dict(job_config)},
            {"field": "job_metadata", "observed": dict(job_metadata)},
            {"field": "top_error_signatures", "observed": dict(error_signatures.most_common(5))},
            {"field": "failed_page_samples", "observed": samples},
        ],
        metrics={
            "job_id": job_id,
            "job_status": job.get("status"),
            "observed_page_count": total_observed,
            "failed_count": len(failed),
            "failure_rate": failure_rate,
            "navigation_count": len(navigation),
            "failed_navigation_count": len(failed_navigation),
            "failed_resource_count": len(failed_resources),
            "renderer_error_count": len(renderer_failures),
            "no_http_response_count": len(no_http_response),
            "non_retryable_count": len(non_retryable),
            "http_failure_count": len(http_failures),
            "dominant_error_code": error_codes.most_common(1)[0][0] if error_codes else None,
            "error_code_distribution": dict(error_codes),
            "render_js": job_config.get("render_js"),
            "sample_limit": sample_pages,
        },
        warnings=warnings,
        recommended_actions=actions,
        confidence="observed" if failed else "insufficient_data",
        classification=classification,
    )
