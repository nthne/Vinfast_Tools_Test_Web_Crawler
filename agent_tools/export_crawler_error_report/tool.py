"""Write a human-readable local Markdown report for crawler failures."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit

from crawler_client.schemas import CrawledPage

from ..diagnose_failed_pages.tool import _error_code, _error_message, _failure_payload, _metadata
from ..models import ToolResult


def _safe_url(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}" if parsed.netloc else parsed.path


def _cell(value: Any) -> str:
    text = "-" if value is None or value == "" else str(value)
    return text.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _failure_classification(failed: list[CrawledPage], navigation: list[CrawledPage]) -> str:
    renderer_failures = [
        page
        for page in failed
        if any(marker in _error_message(page).casefold() for marker in ("js_escalation_failed", "cdp", "renderer error"))
    ]
    http_failures = [page for page in failed if page.status_code is not None]
    if not failed:
        return "NO_FAILURES"
    if len(renderer_failures) / len(failed) >= 0.8:
        return "RENDERER_INFRASTRUCTURE_FAILURE"
    if http_failures and len(http_failures) == len(failed):
        return "HTTP_FAILURE"
    if len(failed) == len(navigation):
        return "SYSTEMIC_FAILURE"
    return "MIXED_FAILURE"


def _recommended_actions(failed: list[CrawledPage]) -> list[str]:
    renderer_failures = [
        page
        for page in failed
        if any(marker in _error_message(page).casefold() for marker in ("js_escalation_failed", "cdp", "renderer error"))
    ]
    actions: list[str] = []
    if renderer_failures:
        actions.extend(
            [
                "Kiểm tra log và health của browser/renderer worker tại thời điểm job chạy.",
                "Chạy thử một URL với render_js=false hoặc HTTP-only nếu nội dung không cần JavaScript.",
                "Nếu bắt buộc render JavaScript, sửa lỗi CDP/session trước khi crawl lại.",
            ]
        )
    if any(page.status_code is None for page in failed):
        actions.append("Không kết luận site trả 4xx/5xx; một số lỗi xảy ra trước khi crawler ghi nhận HTTP response.")
    return actions or ["Kiểm tra failure detail và retry policy trước khi retry có kiểm soát."]


def _job_config_rows(config: dict[str, Any]) -> str:
    rows = ["| Config | Value |", "|---|---|"]
    for key in sorted(config):
        if key.casefold() in {"password", "token", "cookie", "authorization", "api_key"}:
            value = "***"
        else:
            value = config[key]
        rows.append(f"| {_cell(key)} | {_cell(value)} |")
    return "\n".join(rows)


_HISTORY_START = "<!-- CRAWLER_ERROR_HISTORY_BEGIN"
_HISTORY_END = "CRAWLER_ERROR_HISTORY_END -->"


def _signature_key(code: str, message: str) -> str:
    return hashlib.sha256(f"{code}\n{message}".encode("utf-8")).hexdigest()[:12]


def _signature_filename(code: str, message: str) -> str:
    safe_code = re.sub(r"[^A-Za-z0-9_.-]+", "_", code or "UNKNOWN_ERROR").strip("_") or "UNKNOWN_ERROR"
    return f"{safe_code.lower()}_{_signature_key(code, message)}.md"


def _finding_signature(finding: dict[str, Any]) -> tuple[str, str]:
    metrics = finding.get("metrics") or {}
    code = str(metrics.get("finding_code") or metrics.get("relative_link_root_cause") or "")
    if not code:
        classification = str(finding.get("classification") or "DIAGNOSTIC_FINDING")
        code = f"QA_{classification}"
    messages = {
        "SOURCE_URL_MISSING_TRAILING_SLASH": "Relative links resolve against a source URL without a trailing slash",
    }
    return code, messages.get(code, str(finding.get("answer") or "Diagnostic finding"))


def _finding_summary_lines(finding: dict[str, Any], detail_path: str) -> list[str]:
    code = str(finding.get("code") or "DIAGNOSTIC_FINDING")
    metrics = finding.get("metrics") or {}
    if code == "SOURCE_URL_MISSING_TRAILING_SLASH":
        source_url = _safe_url(str(metrics.get("source_url") or "-"))
        bad_url = _safe_url(str(metrics.get("relative_resolution_without_slash") or "-"))
        good_url = _safe_url(str(metrics.get("relative_resolution_with_slash") or "-"))
        return [
            "**Giải thích:** Source URL đang thiếu dấu `/` cuối, nên crawler xử lý nó như một path dạng file khi resolve các link tương đối.",
            "",
            f"**Bằng chứng:** Source `{source_url}` tạo ra URL `{bad_url}` thay vì `{good_url}`. URL sai trả HTTP 404, trong khi URL hiện hành trả HTTP 200.",
            "",
            "**Ảnh hưởng:** Các tài liệu dùng relative link có thể bị chuyển thành đường dẫn sai và bị đánh dấu lỗi. Đây là lỗi xử lý base URL/redirect của crawler, không phải tài liệu PyTorch bị mất.",
            "",
            "**Khuyến nghị:** Cấu hình source với dấu `/` cuối hoặc dùng URL version cụ thể; crawler nên resolve link dựa trên `final_url` sau redirect.",
            "",
            f"**Report chi tiết:** [{_cell(detail_path)}]({_cell(detail_path)})",
        ]
    if code == "OUT_OF_SCOPE_URL_LEAK":
        return [
            "**Giải thích:** Crawler đã đưa URL ngoài scope của source vào kết quả. Một số resource URL trả về HTML (`text/html`) nhưng vẫn bị parse link và tiếp tục mở rộng queue; đồng thời navigation allowlist chưa chặn được domain ngoài source.",
            "",
            f"**Bằng chứng:** {_cell(finding.get('answer') or 'Observed external page/link records outside the source scope.')}",
            "",
            "**Ảnh hưởng:** Crawl có thể thu thập nội dung không liên quan, biến resource thành nguồn phát sinh page/link mới, làm tăng URL expansion và tiêu thụ page/resource budget.",
            "",
            "**Khuyến nghị:** Chặn external navigation trước khi enqueue; không parse/follow link từ resource trả HTML; ghi nhận MIME/kind mismatch và canonicalize URL trước khi đưa vào queue.",
            "",
            f"**Report chi tiết:** [{_cell(detail_path)}]({_cell(detail_path)})",
        ]
    return [
        f"**Giải thích:** {_cell(finding.get('message') or 'Diagnostic finding')}",
        "",
        f"**Bằng chứng:** {_cell(finding.get('answer') or 'No additional explanation was recorded.')}",
        "",
        f"**Report chi tiết:** [{_cell(detail_path)}]({_cell(detail_path)})",
    ]


def _load_history(summary_path: Path) -> dict[str, Any]:
    if not summary_path.exists():
        return {"runs": []}
    text = summary_path.read_text(encoding="utf-8")
    start = text.find(_HISTORY_START)
    end = text.find(_HISTORY_END, start + len(_HISTORY_START)) if start >= 0 else -1
    if start < 0 or end < 0:
        return {"runs": []}
    payload = text[start + len(_HISTORY_START):end].strip()
    try:
        history = json.loads(payload)
    except json.JSONDecodeError:
        return {"runs": []}
    return history if isinstance(history, dict) and isinstance(history.get("runs"), list) else {"runs": []}


def _write_summary(summary_path: Path, history: dict[str, Any]) -> None:
    runs = history.get("runs") or []
    totals: dict[str, dict[str, Any]] = {}
    for run in runs:
        for group in run.get("error_groups") or []:
            signature = str(group.get("signature"))
            item = totals.setdefault(
                signature,
                {
                    "code": group.get("code"),
                    "message": group.get("message"),
                    "total_count": 0,
                    "job_ids": set(),
                    "first_seen": run.get("generated_at"),
                    "last_seen": run.get("generated_at"),
                    "detail_path": group.get("detail_path"),
                },
            )
            item["total_count"] += int(group.get("count") or 0)
            item["job_ids"].add(str(run.get("job_id")))
            item["first_seen"] = min(item["first_seen"] or run.get("generated_at"), run.get("generated_at") or item["first_seen"])
            item["last_seen"] = max(item["last_seen"] or run.get("generated_at"), run.get("generated_at") or item["last_seen"])
            item["detail_path"] = group.get("detail_path") or item["detail_path"]

    finding_totals: dict[str, dict[str, Any]] = {}
    for finding in history.get("findings") or []:
        signature = str(finding.get("signature"))
        item = finding_totals.setdefault(
            signature,
            {
                "code": finding.get("code"),
                "message": finding.get("message"),
                "total_count": 0,
                "job_ids": set(),
                "detail_path": finding.get("detail_path"),
                "metrics": finding.get("metrics") or {},
                "evidence": finding.get("evidence") or [],
                "answer": finding.get("answer") or "",
            },
        )
        item["total_count"] += int(finding.get("count") or 0)
        item["job_ids"].add(str(finding.get("job_id")))
        item["detail_path"] = finding.get("detail_path") or item["detail_path"]

    visible = [
        "# Crawler Error Summary",
        "",
        "> Cumulative, concise summary of error signatures observed by the report tool.",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Unique crawl jobs | {len(runs)} |",
        f"| Error signatures | {len(totals)} |",
        f"| Total failed-page observations | {sum(item['total_count'] for item in totals.values())} |",
        f"| Additional QA findings | {len(finding_totals)} |",
        f"| Last updated (UTC) | `{_cell(max((run.get('generated_at') or '') for run in runs) if runs else '-')}` |",
        "",
        "## Error types",
        "",
        "| Rank | Error code | Short message | Total pages | Jobs | Detail report |",
        "|---:|---|---|---:|---:|---|",
    ]
    ordered = sorted(totals.values(), key=lambda item: (-item["total_count"], str(item["code"])))
    if ordered:
        for rank, item in enumerate(ordered, start=1):
            detail = item.get("detail_path") or "-"
            visible.append(
                f"| {rank} | `{_cell(item['code'])}` | {_cell(item['message'])} | {item['total_count']} | "
                f"{len(item['job_ids'])} | [{_cell(detail)}]({_cell(detail)}) |"
            )
    else:
        visible.append("| - | - | No errors recorded | 0 | 0 | - |")
    visible.extend(["", "## Additional QA findings", ""])
    ordered_findings = sorted(finding_totals.values(), key=lambda item: (-item["total_count"], str(item["code"])))
    if ordered_findings:
        for item in ordered_findings:
            visible.append(f"### `{_cell(item['code'])}`")
            visible.append("")
            visible.extend(_finding_summary_lines(item, item.get("detail_path") or "-"))
            visible.append("")
    else:
        visible.append("Không có additional QA finding nào được ghi nhận.")
    visible.extend(["", "## Crawl runs", "", "| Job ID | Source ID | Classification | Observed pages | Failed pages | Generated |", "|---|---|---|---:|---:|---|"])
    for run in sorted(runs, key=lambda item: str(item.get("generated_at") or ""), reverse=True):
        visible.append(
            f"| `{_cell(run.get('job_id'))}` | `{_cell(run.get('source_id'))}` | `{_cell(run.get('classification'))}` | "
            f"{run.get('observed_page_count', 0)} | {run.get('failed_count', 0)} | `{_cell(run.get('generated_at'))}` |"
        )
    visible.extend([
        "",
        "## How to use",
        "",
        "- Open the linked detail report for the full evidence and affected page list.",
        "- Send this file together with the relevant detail reports to crawler developers.",
        "- Counts are deduplicated by job ID when the same job is reported again.",
        "",
        _HISTORY_START,
        json.dumps(history, ensure_ascii=False, indent=2, sort_keys=True),
        _HISTORY_END,
        "",
    ])
    summary_path.write_text("\n".join(visible), encoding="utf-8")


def _write_finding_detail(path: Path, finding: dict[str, Any], code: str, message: str, generated_at: str) -> None:
    metrics = finding.get("metrics") or {}
    evidence = finding.get("evidence") or []
    actions = finding.get("recommended_actions") or []
    lines = [
        "# Detailed Crawler Diagnostic Report",
        "",
        f"## Finding: `{_cell(code)}`",
        "",
        f"**Message:** {_cell(message)}",
        "",
        "## Impact",
        "",
        "This is a crawler QA diagnostic finding. It is reported separately from page-failure counts.",
        "",
        "| Metric | Value |",
        "|---|---|",
    ]
    for key, value in metrics.items():
        lines.append(f"| `{_cell(key)}` | `{_cell(_safe_url(str(value)) if isinstance(value, str) else value)}` |")
    lines.extend(["", "## Observed evidence", ""])
    if evidence:
        for index, item in enumerate(evidence, start=1):
            lines.append(f"### Observation {index}")
            lines.append("")
            for key, value in item.items():
                safe_value = _safe_url(str(value)) if isinstance(value, str) and (key.endswith("url") or "url" in key) else value
                lines.append(f"- `{_cell(key)}`: `{_cell(safe_value)}`")
            lines.append("")
    else:
        lines.append("No page-level evidence was returned.")
        lines.append("")
    lines.extend(["## Recommended actions", ""])
    if actions:
        lines.extend(f"{index}. {action}" for index, action in enumerate(actions, start=1))
    else:
        lines.append("Review the source URL, redirect handling, and relative-link resolution logic.")
    lines.extend([
        "",
        "## Safety",
        "",
        "- This finding was recorded from read-only crawler/API and upstream probes.",
        "- Query strings and fragments are omitted from URL evidence.",
        "- No retry, cancel, delete, or crawler configuration mutation was performed.",
        f"- Generated at (UTC): `{generated_at}`",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_error_detail(
    path: Path,
    job: dict[str, Any],
    job_id: str,
    code: str,
    message: str,
    pages: list[CrawledPage],
    total_failed: int,
    generated_at: str,
) -> None:
    kind_counts = Counter(str(_metadata(page).get("kind") or "UNKNOWN") for page in pages)
    status_counts = Counter(str(page.status_code) if page.status_code is not None else "NO_HTTP_STATUS" for page in pages)
    retryable_counts = Counter(str(_failure_payload(page).get("retryable")) for page in pages)
    lines = [
        "# Detailed Crawler Error Report",
        "",
        f"## Error signature: `{_cell(code)}`",
        "",
        f"**Message:** {_cell(message)}",
        "",
        "## Impact",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Job ID | `{_cell(job_id)}` |",
        f"| Source ID | `{_cell(job.get('source_id'))}` |",
        f"| Pages with this error in this job | {len(pages)} |",
        f"| All failed pages in this job | {total_failed} |",
        f"| Share of failed pages | {len(pages) / total_failed:.1%} |" if total_failed else "| Share of failed pages | 0.0% |",
        f"| Generated at (UTC) | `{generated_at}` |",
        "",
        "## Evidence",
        "",
        f"- Status/kind distribution: `{dict(kind_counts)}`",
        f"- HTTP status distribution: `{dict(status_counts)}`",
        f"- Retryable distribution: `{dict(retryable_counts)}`",
        f"- Runtime crawl config: `{job.get('crawl_config') or {}}`",
        "",
        "## Affected pages",
        "",
        "| # | Page ID | Kind | HTTP status | Retryable | URL |",
        "|---:|---|---|---:|---|---|",
    ]
    for index, page in enumerate(pages, start=1):
        lines.append(
            f"| {index} | `{_cell(page.page_id)}` | `{_cell(_metadata(page).get('kind'))}` | {_cell(page.status_code)} | "
            f"{_cell(_failure_payload(page).get('retryable'))} | `{_cell(_safe_url(page.url))}` |"
        )
    lines.extend([
        "",
        "## Recommended checks",
        "",
        "1. Correlate this error message with crawler worker logs at the job timestamp.",
        "2. Check whether the failure occurred before an HTTP response was recorded.",
        "3. Verify retryability and whether the error was incorrectly marked permanent.",
        "4. Reproduce with one page before starting a full recrawl.",
        "",
        "## Safety",
        "",
        "- URLs omit query strings and fragments.",
        "- This report was generated from read-only crawler API calls.",
        "- No retry, cancel, delete, or crawler configuration mutation was performed.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def export_crawler_error_report(
    client: Any,
    job_id: str,
    output_path: str | Path | None = None,
    sample_pages: int | None = None,
    max_page_rows: int = 200,
    output_dir: str | Path | None = None,
    summary_path: str | Path | None = None,
    diagnostic_findings: list[dict[str, Any]] | None = None,
) -> ToolResult:
    """Write per-error detail reports and update one cumulative Markdown summary."""

    job = client.get_job(job_id)
    pages = client.list_pages(job_id=job_id, limit=sample_pages)
    failed = [page for page in pages if str(_metadata(page).get("status") or "").upper() == "FAILED"]
    navigation = [page for page in pages if str(_metadata(page).get("kind") or "").upper() == "NAVIGATION"]
    renderer_failures = [
        page
        for page in failed
        if any(marker in _error_message(page).casefold() for marker in ("js_escalation_failed", "cdp", "renderer error"))
    ]
    no_http = [page for page in failed if page.status_code is None]
    non_retryable = [page for page in failed if _failure_payload(page).get("retryable") is False]
    http_failures = [page for page in failed if page.status_code is not None]
    status_counts = Counter(str(_metadata(page).get("status") or "UNKNOWN") for page in pages)
    kind_counts = Counter(str(_metadata(page).get("kind") or "UNKNOWN") for page in pages)
    error_groups = Counter((_error_code(page), _error_message(page)) for page in failed)
    classification = _failure_classification(failed, navigation)
    failure_rate = len(failed) / len(pages) if pages else 0.0

    legacy_output = Path(output_path) if output_path is not None else None
    report_root = Path(output_dir) if output_dir is not None else (legacy_output.parent if legacy_output else Path("artifacts/crawler_error_reports"))
    detail_dir = report_root / "errors"
    summary = Path(summary_path) if summary_path is not None else report_root / "crawler_error_summary.md"
    if legacy_output:
        legacy_output.parent.mkdir(parents=True, exist_ok=True)
    detail_dir.mkdir(parents=True, exist_ok=True)
    summary.parent.mkdir(parents=True, exist_ok=True)

    written_pages = failed[: max(0, max_page_rows)]
    omitted_pages = max(0, len(failed) - len(written_pages))
    generated_at = datetime.now(timezone.utc).isoformat()
    lines = [
        "# Crawler Error Report",
        "",
        "> Human-readable, read-only QA summary for crawler developers.",
        "",
        "## 1. Executive summary",
        "",
        f"**Conclusion:** `{classification}`",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Job ID | `{_cell(job_id)}` |",
        f"| Source ID | `{_cell(job.get('source_id'))}` |",
        f"| Job status | `{_cell(job.get('status'))}` |",
        f"| Observed pages | {len(pages)} |",
        f"| Failed pages | {len(failed)} |",
        f"| Failure rate | {failure_rate:.1%} |",
        f"| Renderer/CDP failures | {len(renderer_failures)} |",
        f"| Failed without HTTP status | {len(no_http)} |",
        f"| HTTP failures | {len(http_failures)} |",
        f"| Non-retryable failures | {len(non_retryable)} |",
        f"| Generated at (UTC) | `{generated_at}` |",
        "",
        "## 2. What this means",
        "",
    ]
    if renderer_failures:
        lines.extend([
            "The dominant failures contain renderer/CDP signatures such as `js_escalation_failed`, `CDP`, or `WS closed`.",
            "These pages have no recorded HTTP status, so this report does **not** classify them as target-site 4xx/5xx responses.",
        ])
    elif http_failures and len(http_failures) == len(failed):
        lines.append("All failed pages have an HTTP status; investigate target responses, retry policy, and access controls.")
    else:
        lines.append("The failure set is mixed; use the error distribution and affected-page table for follow-up.")
    lines.extend(["", "## 3. Error distribution", "", "| Rank | Error code | Message | Count | Share of failures |", "|---:|---|---|---:|---:|"])
    for rank, ((code, message), count) in enumerate(error_groups.most_common(), start=1):
        lines.append(f"| {rank} | `{_cell(code)}` | {_cell(message)} | {count} | {count / len(failed):.1%} |")
    if not error_groups:
        lines.append("| - | - | No failed pages observed | 0 | 0.0% |")

    lines.extend(["", "## 4. Distribution by status and kind", "", "### Status", "", "| Status | Count |", "|---|---:|"])
    lines.extend(f"| `{_cell(key)}` | {value} |" for key, value in status_counts.most_common())
    lines.extend(["", "### Kind", "", "| Kind | Count |", "|---|---:|"])
    lines.extend(f"| `{_cell(key)}` | {value} |" for key, value in kind_counts.most_common())

    lines.extend(["", "## 5. Affected pages", "", f"Showing {len(written_pages)} of {len(failed)} failed pages.", "", "| # | Page ID | Kind | HTTP status | Error code | URL |", "|---:|---|---|---:|---|---|"])
    for index, page in enumerate(written_pages, start=1):
        lines.append(
            f"| {index} | `{_cell(page.page_id)}` | `{_cell(_metadata(page).get('kind'))}` | "
            f"{_cell(page.status_code)} | `{_cell(_error_code(page))}` | `{_cell(_safe_url(page.url))}` |"
        )
    if omitted_pages:
        lines.extend(["", f"> {omitted_pages} failed page rows were omitted by `max_page_rows={max_page_rows}`."])

    lines.extend(["", "## 6. Runtime configuration", "", _job_config_rows(job.get("crawl_config") or {})])
    lines.extend(["", "## 7. Recommended actions", ""])
    lines.extend(f"{index}. {action}" for index, action in enumerate(_recommended_actions(failed), start=1))
    lines.extend(["", "## 8. Report scope and safety", "", "- This report was generated from read-only crawler API calls.", "- Page query strings/fragments are removed from URLs to avoid leaking signed parameters or tokens.", "- No retry, cancel, delete, source update, or crawler configuration mutation was performed.", ""])
    if legacy_output:
        legacy_output.write_text("\n".join(lines), encoding="utf-8")

    detail_paths: list[str] = []
    error_history_groups: list[dict[str, Any]] = []
    for (code, message), count in error_groups.items():
        detail_path = detail_dir / _signature_filename(code, message)
        group_pages = [page for page in failed if (_error_code(page), _error_message(page)) == (code, message)]
        _write_error_detail(detail_path, job, job_id, code, message, group_pages, len(failed), generated_at)
        detail_paths.append(str(detail_path))
        try:
            relative_detail_path = detail_path.relative_to(summary.parent).as_posix()
        except ValueError:
            relative_detail_path = str(detail_path)
        error_history_groups.append(
            {
                "signature": _signature_key(code, message),
                "code": code,
                "message": message,
                "count": count,
                "detail_path": relative_detail_path,
            }
        )

    history = _load_history(summary)
    history["runs"] = [run for run in history.get("runs", []) if str(run.get("job_id")) != str(job_id)]
    history["runs"].append(
        {
            "job_id": job_id,
            "source_id": job.get("source_id"),
            "classification": classification,
            "observed_page_count": len(pages),
            "failed_count": len(failed),
            "generated_at": generated_at,
            "error_groups": error_history_groups,
        }
    )
    diagnostic_detail_paths: list[str] = []
    if diagnostic_findings is None:
        existing_findings = list(history.get("findings", []))
    else:
        existing_findings = [
            finding
            for finding in history.get("findings", [])
            if str(finding.get("job_id")) != str(job_id)
        ]
    for finding in diagnostic_findings or []:
        code, message = _finding_signature(finding)
        detail_path = detail_dir / _signature_filename(code, message)
        _write_finding_detail(detail_path, finding, code, message, generated_at)
        diagnostic_detail_paths.append(str(detail_path))
        try:
            relative_detail_path = detail_path.relative_to(summary.parent).as_posix()
        except ValueError:
            relative_detail_path = str(detail_path)
        metrics = finding.get("metrics") or {}
        existing_findings.append(
            {
                "signature": _signature_key(code, message),
                "code": code,
                "message": message,
                "count": int(metrics.get("mismatch_count") or 1),
                "job_id": job_id,
                "source_id": job.get("source_id"),
                "detail_path": relative_detail_path,
                "generated_at": generated_at,
                "metrics": metrics,
                "evidence": finding.get("evidence") or [],
                "answer": finding.get("answer") or "",
            }
        )
    history["findings"] = existing_findings
    _write_summary(summary, history)

    return ToolResult(
        tool_name="export_crawler_error_report",
        answer=(
            f"Wrote {len(detail_paths)} detailed error reports and "
            f"{len(diagnostic_detail_paths)} diagnostic reports; updated the cumulative summary at {summary}."
        ),
        evidence=[
            {"field": "report_path", "observed": str(legacy_output) if legacy_output else None},
            {"field": "detail_report_paths", "observed": detail_paths},
            {"field": "summary_path", "observed": str(summary)},
            {"field": "diagnostic_detail_report_paths", "observed": diagnostic_detail_paths},
            {"field": "classification", "observed": classification},
            {"field": "error_groups", "observed": {f"{code}: {message}": count for (code, message), count in error_groups.items()}},
        ],
        metrics={
            "job_id": job_id,
            "observed_page_count": len(pages),
            "failed_count": len(failed),
            "failure_rate": failure_rate,
            "renderer_error_count": len(renderer_failures),
            "no_http_response_count": len(no_http),
            "report_path": str(legacy_output) if legacy_output else None,
            "detail_report_paths": detail_paths,
            "summary_path": str(summary),
            "diagnostic_detail_report_paths": diagnostic_detail_paths,
            "report_line_count": len(lines),
            "affected_rows_written": len(written_pages),
            "affected_rows_omitted": omitted_pages,
            "local_file_written": True,
        },
        warnings=["LOCAL_ERROR_REPORTS_WRITTEN", "CUMULATIVE_SUMMARY_UPDATED"],
        recommended_actions=["Gửi file Markdown này cho đội phát triển crawler kèm job ID và thời điểm chạy."],
        classification=classification,
    )
