"""Audit historical crawler jobs and explain failure causes in natural language."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from crawler_client.schemas import CrawledPage

from ..diagnose_crawl_stall.tool import _url_route
from ..diagnose_failed_pages.tool import _error_code, _error_message, _failure_payload, _metadata
from ..models import ToolResult


def _safe_url(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}" if parsed.netloc else parsed.path


def _job_day(value: Any) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _category(code: str, message: str) -> tuple[str, str, str]:
    text = f"{code} {message}".casefold()
    if "temporary" in text or "retry" in text or "retries exhausted" in text:
        return (
            "Retry exhausted",
            "Crawler đã thử lại nhưng số lần retry vẫn hết trước khi renderer/download hoàn tất.",
            "Kiểm tra retry policy, giới hạn concurrency và lỗi gốc trước khi tăng retry vô hạn.",
        )
    if "js_escalation_failed" in text or "cdp" in text or "renderer error" in text or "no js renderer" in text:
        return (
            "Renderer/CDP",
            "Browser renderer hoặc phiên CDP của crawler không sẵn sàng; lỗi xảy ra trước khi có HTTP response đáng tin cậy.",
            "Kiểm tra health/worker capacity của renderer; thử HTTP-only nếu trang không cần JavaScript.",
        )
    if "no_proxy_available" in text or ("http_403" in text and "proxy" in text):
        return (
            "proxy/403",
            "Crawler không có proxy phù hợp hoặc upstream trả 403 cho đường đi hiện tại.",
            "Kiểm tra proxy pool, host policy và quyền truy cập; không coi đây là lỗi extraction.",
        )
    if "anti-bot" in text or "generic_block" in text or "access denied" in text:
        return (
            "Anti-bot/403",
            "Trang đích hoặc CDN trả trang chặn bot/403 thay vì nội dung tài liệu.",
            "Kiểm tra authenticated/browser crawl và anti-bot policy; không bypass CAPTCHA tự động.",
        )
    if "unsafe" in text or "dns" in text or "connected peer differs" in text or "ssrf" in text:
        return (
            "SSRF/DNS security",
            "Crawler chặn download vì host không nằm trong allowlist hoặc DNS/peer không khớp kiểm tra an toàn.",
            "Xác minh host hợp lệ rồi cập nhật allowlist/SSRF policy theo cách an toàn.",
        )
    if "451" in text:
        return (
            "Download HTTP 451",
            "Upstream từ chối cung cấp resource vì hạn chế pháp lý, khu vực hoặc chính sách truy cập.",
            "Kiểm tra quyền truy cập và geography của endpoint; không retry vô hạn.",
        )
    if "404" in text:
        return (
            "Download HTTP 404",
            "Resource URL được crawler yêu cầu không tồn tại tại thời điểm kiểm tra.",
            "Kiểm tra URL extraction/canonicalization và phân biệt resource 404 với page 404.",
        )
    if "400" in text:
        return (
            "Upstream/request 400",
            "Target hoặc request tạo ra URL/params mà upstream không chấp nhận.",
            "Kiểm tra URL normalization, query parameters và redirect chain.",
        )
    if "structural" in text or "no usable content" in text:
        return (
            "Extraction/HTML structure",
            "Crawler nhận được shell HTML, body thiếu hoặc nội dung quá ít để extraction tạo page hợp lệ.",
            "So sánh raw HTML với rendered DOM và kiểm tra selector/content extraction rule.",
        )
    return (
        "Other crawler failure",
        "Failure chưa khớp heuristic cụ thể; cần đối chiếu worker log và raw failure detail.",
        "Mở detail report theo error signature và tái hiện bằng một URL nhỏ.",
    )


def _job_snapshot(job: dict[str, Any], pages: list[CrawledPage]) -> dict[str, Any]:
    failed = [page for page in pages if str(_metadata(page).get("status") or "").upper() == "FAILED"]
    signatures = Counter((_error_code(page), _error_message(page)) for page in failed)
    categories: Counter[str] = Counter()
    category_details: dict[str, tuple[str, str]] = {}
    for (code, message), count in signatures.items():
        category, reason, action = _category(code, message)
        categories[category] += count
        category_details[category] = (reason, action)

    urls = [str(page.url) for page in pages if page.url]
    exact_duplicates = sum(1 for count in Counter(urls).values() if count > 1)
    route_variants = sum(1 for count in Counter(_url_route(url) for url in urls).values() if count > 1)
    expansion_count = sum(
        1
        for url in urls
        if len(url) > 1000 or any(count >= 3 for count in Counter(part for part in urlsplit(url).path.split("/") if part).values())
    )
    config = job.get("crawl_config") or {}
    metadata = job.get("metadata") or {}
    max_pages = config.get("max_pages")
    max_resources = config.get("max_resources")
    budget = max_pages + max_resources if isinstance(max_pages, int) and isinstance(max_resources, int) else None
    metadata_failed = metadata.get("failed_count")
    metadata_total = metadata.get("total_pages")
    return {
        "job": job,
        "pages": pages,
        "failed": failed,
        "signatures": signatures,
        "categories": categories,
        "category_details": category_details,
        "navigation_count": sum(str(_metadata(page).get("kind") or "").upper() == "NAVIGATION" for page in pages),
        "resource_count": sum(str(_metadata(page).get("kind") or "").upper() == "RESOURCE" for page in pages),
        "resource_content_types": Counter(
            (str(page.content_type or "UNKNOWN").lower())
            for page in pages
            if str(_metadata(page).get("kind") or "").upper() == "RESOURCE"
        ),
        "exact_duplicate_groups": exact_duplicates,
        "route_variant_groups": route_variants,
        "url_expansion_count": expansion_count,
        "effective_budget": budget,
        "metadata_failed": metadata_failed,
        "metadata_total": metadata_total,
        "metadata_failed_mismatch": isinstance(metadata_failed, int) and metadata_failed != len(failed),
        "metadata_total_mismatch": isinstance(metadata_total, int) and metadata_total != len(pages),
    }


def _job_reason_lines(snapshot: dict[str, Any]) -> list[str]:
    job = snapshot["job"]
    lines: list[str] = []
    if not snapshot["failed"]:
        lines.append("**Kết luận:** Không có page failed trong dữ liệu page endpoint của job này.")
    for category, count in snapshot["categories"].most_common():
        reason, action = snapshot["category_details"][category]
        lines.extend([
            f"- **Lý do ({category}, {count} record):** {reason}",
            f"  - **Nên kiểm tra:** {action}",
        ])
    if snapshot["url_expansion_count"] or snapshot["exact_duplicate_groups"] or snapshot["route_variant_groups"]:
        lines.append(
            f"- **Lý do URL/budget:** phát hiện {snapshot['url_expansion_count']} URL có dấu hiệu path expansion, "
            f"{snapshot['exact_duplicate_groups']} nhóm URL trùng và {snapshot['route_variant_groups']} nhóm route biến thể trong page sample/toàn job."
        )
        lines.append("  - **Nên kiểm tra:** URL canonicalization, pagination/calendar trap và việc resource URL có bị đưa vào navigation queue hay không.")
    if snapshot["resource_count"]:
        image_count = sum(count for content_type, count in snapshot["resource_content_types"].items() if content_type.startswith("image/"))
        image_ratio = image_count / snapshot["resource_count"]
        lines.append(
            f"- **Resource mix:** {snapshot['resource_count']} resource record; {image_count} có MIME image ({image_ratio:.1%}). "
            "Resource ảnh thường là asset hợp lệ, nhưng không nên bị tính như navigation page hoặc làm cạn resource budget ngoài dự kiến."
        )
    if snapshot["metadata_failed_mismatch"] or snapshot["metadata_total_mismatch"]:
        lines.append(
            f"- **Lý do số liệu:** job metadata báo total={snapshot['metadata_total']}, failed={snapshot['metadata_failed']} "
            f"nhưng page endpoint trả total={len(snapshot['pages'])}, failed={len(snapshot['failed'])}; cần kiểm tra consistency giữa hai API."
        )
    if str(job.get("status") or "").upper() == "CANCELLED":
        lines.append("- **Trạng thái:** Job bị CANCELLED; các lỗi còn lại không thể dùng để đánh giá toàn bộ source như một crawl hoàn tất.")
    return lines or ["- **Lý do:** Chưa có đủ failure evidence để kết luận thêm."]


def _write_report(path: Path, snapshots: list[dict[str, Any]], start_date: str | None, end_date: str | None) -> None:
    category_aggregate: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "jobs": set(), "reason": "", "action": ""})
    for snapshot in snapshots:
        for category, count in snapshot["categories"].items():
            item = category_aggregate[category]
            item["count"] += count
            item["jobs"].add(str(snapshot["job"].get("id")))
            item["reason"], item["action"] = snapshot["category_details"][category]

    lines = [
        "# Crawl History Audit",
        "",
        f"> Phân tích read-only các job crawl từ `{start_date or '-'}` đến `{end_date or '-'}`.",
        "",
        "## Kết luận tổng quát",
        "",
        f"Đã kiểm tra **{len(snapshots)} job**. Report phân biệt lỗi renderer/crawler, lỗi upstream/access, lỗi extraction và lỗi URL expansion; không coi mọi `FAILED` là lỗi website.",
        "",
        "## Nhóm nguyên nhân",
        "",
        "| Nhóm | Số record lỗi | Số job | Lý do | Hướng xử lý |",
        "|---|---:|---:|---|---|",
    ]
    for category, item in sorted(category_aggregate.items(), key=lambda pair: (-pair[1]["count"], pair[0])):
        lines.append(f"| **{category}** | {item['count']} | {len(item['jobs'])} | {item['reason']} | {item['action']} |")
    if not category_aggregate:
        lines.append("| - | - | - | Không có failure record | - |")

    lines.extend([
        "",
        "## Chi tiết từng job",
        "",
        "| Job | Source | Bắt đầu | Trạng thái | Page records | Failed records | Kết luận |",
        "|---|---|---|---|---:|---:|---|",
    ])
    for snapshot in sorted(snapshots, key=lambda item: str(item["job"].get("started_at") or "")):
        job = snapshot["job"]
        if snapshot["categories"]:
            conclusion = ", ".join(f"{name} ({count})" for name, count in snapshot["categories"].most_common(3))
        else:
            conclusion = "NO_FAILURES"
        lines.append(
            f"| `{job.get('id')}` | `{job.get('source_id')}` | `{job.get('started_at')}` | `{job.get('status')}` | "
            f"{len(snapshot['pages'])} | {len(snapshot['failed'])} | {conclusion} |"
        )
        lines.extend(["", f"### Job `{job.get('id')}`", "", *_job_reason_lines(snapshot), ""])
        lines.extend(["**Error signatures:**", "", "| Code | Message | Count |", "|---|---|---:|"])
        for (code, message), count in snapshot["signatures"].most_common():
            lines.append(f"| `{code}` | {message or '-'} | {count} |")
        if not snapshot["signatures"]:
            lines.append("| - | Không có error signature | 0 |")
        lines.append("")

    lines.extend([
        "## Ghi chú đọc số liệu",
        "",
        "- `page records` và `failed records` được tính từ page endpoint; job metadata có thể lệch và được ghi riêng trong chi tiết job.",
        "- Lỗi không có HTTP status thường xảy ra trước response, nên không được kết luận là website trả 4xx/5xx.",
        "- Job CANCELLED được giữ lại để giải thích nguyên nhân dừng, nhưng không được coi là crawl hoàn tất.",
        "- Report không retry, cancel, update hoặc delete dữ liệu crawler.",
        "",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def audit_crawl_history(
    client: Any,
    source_keywords: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    output_path: str | Path | None = None,
    include_cancelled: bool = True,
) -> ToolResult:
    """Audit historical jobs for selected sources and date range."""

    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    keywords = [item.casefold() for item in (source_keywords or [])]
    selected_sources = []
    for source in client.list_sources():
        haystack = f"{source.get('name') or ''} {source.get('domain') or ''}".casefold()
        if not keywords or any(keyword in haystack for keyword in keywords):
            selected_sources.append(source)

    snapshots: list[dict[str, Any]] = []
    for source in selected_sources:
        for listed_job in client.list_jobs(source_id=str(source.get("id"))):
            job_id = str(listed_job.get("id") or "")
            if not job_id:
                continue
            job = client.get_job(job_id)
            day = _job_day(job.get("started_at") or listed_job.get("started_at"))
            if start and (day is None or day < start):
                continue
            if end and (day is None or day > end):
                continue
            if not include_cancelled and str(job.get("status") or "").upper() == "CANCELLED":
                continue
            pages = client.list_pages(job_id=job_id)
            snapshots.append(_job_snapshot(job, pages))

    default_name = f"crawl_history_audit_{start_date or 'all'}_{end_date or 'all'}.md"
    report_path = Path(output_path) if output_path is not None else Path("artifacts/crawler_error_reports") / default_name
    _write_report(report_path, snapshots, start_date, end_date)
    aggregate = Counter()
    category_reasons: dict[str, str] = {}
    for snapshot in snapshots:
        aggregate.update(snapshot["categories"])
        for category, (reason, _) in snapshot["category_details"].items():
            category_reasons[category] = reason
    return ToolResult(
        tool_name="audit_crawl_history",
        answer=f"Audited {len(snapshots)} historical crawl jobs and wrote {report_path}.",
        evidence=[
            {"field": "selected_sources", "observed": selected_sources},
            {"field": "job_ids", "observed": [snapshot["job"].get("id") for snapshot in snapshots]},
            {"field": "category_reasons", "observed": category_reasons},
        ],
        metrics={
            "job_count": len(snapshots),
            "source_count": len(selected_sources),
            "total_page_records": sum(len(snapshot["pages"]) for snapshot in snapshots),
            "total_failed_records": sum(len(snapshot["failed"]) for snapshot in snapshots),
            "category_counts": dict(aggregate),
            "report_path": str(report_path),
            "local_file_written": True,
        },
        warnings=["READ_ONLY_HISTORY_AUDIT", "PAGE_ENDPOINT_USED_FOR_FAILURE_COUNTS"],
        recommended_actions=["Open the audit report and the linked per-signature detail reports before changing crawler configuration."],
        confidence="observed" if snapshots else "insufficient_data",
        classification="HISTORY_AUDITED",
    )
