from __future__ import annotations

from agent_tools.export_crawler_error_report import export_crawler_error_report
from crawler_client.schemas import CrawledPage


class FakeReportClient:
    def __init__(self):
        self.job = {
            "id": "job-report",
            "source_id": "source-report",
            "status": "COMPLETED",
            "started_at": "2026-09-18T01:00:00Z",
            "finished_at": "2026-09-18T01:05:00Z",
            "crawl_config": {"render_js": None, "max_pages": 10, "max_resources": 20},
            "metadata": {"total_pages": 3, "failed_count": 2, "success_count": 1},
        }
        self.pages = [
            CrawledPage(
                page_id="failed-1",
                source_id="source-report",
                job_id="job-report",
                url="https://example.test/a?token=secret",
                metadata={
                    "status": "FAILED",
                    "kind": "NAVIGATION",
                    "failure": {"code": "CRW_PERMANENT", "retryable": False},
                    "error": {"code": "CRW_PERMANENT", "message": "CDP Target.createTarget: WS closed"},
                },
            ),
            CrawledPage(
                page_id="failed-2",
                source_id="source-report",
                job_id="job-report",
                url="https://example.test/b",
                metadata={
                    "status": "FAILED",
                    "kind": "NAVIGATION",
                    "failure": {"code": "CRW_PERMANENT", "retryable": False},
                    "error": {"code": "CRW_PERMANENT", "message": "CDP Target.createTarget: WS closed"},
                },
            ),
            CrawledPage(
                page_id="ok-1",
                source_id="source-report",
                job_id="job-report",
                url="https://example.test/ok",
                status_code=200,
                metadata={"status": "NEW_INFO", "kind": "NAVIGATION"},
            ),
        ]

    def get_job(self, job_id):
        return self.job

    def list_pages(self, job_id=None, limit=None):
        return self.pages[:limit] if limit is not None else self.pages


def test_export_crawler_error_report_writes_readable_markdown_without_query_secrets(tmp_path):
    output_path = tmp_path / "crawler-errors.md"

    result = export_crawler_error_report(FakeReportClient(), "job-report", output_path=output_path)
    report = output_path.read_text(encoding="utf-8")

    assert result.tool_name == "export_crawler_error_report"
    assert result.metrics["failed_count"] == 2
    assert result.metrics["report_path"].endswith("crawler-errors.md")
    assert "# Crawler Error Report" in report
    assert "RENDERER_INFRASTRUCTURE_FAILURE" in report
    assert "CRW_PERMANENT" in report
    assert "failed-1" in report
    assert "?token=secret" not in report


def test_export_crawler_error_report_writes_one_detail_per_signature_and_accumulates_summary(tmp_path):
    client = FakeReportClient()
    client.pages.append(
        CrawledPage(
            page_id="failed-3",
            source_id="source-report",
            job_id="job-report",
            url="https://example.test/server-error",
            status_code=500,
            metadata={
                "status": "FAILED",
                "kind": "NAVIGATION",
                "failure": {"code": "HTTP_500", "retryable": True},
                "error": {"code": "HTTP_500", "message": "origin returned 500"},
            },
        )
    )
    output_dir = tmp_path / "reports"

    export_crawler_error_report(client, "job-report", output_dir=output_dir)
    client.job["id"] = "job-report-2"
    export_crawler_error_report(client, "job-report-2", output_dir=output_dir)

    detail_files = list((output_dir / "errors").glob("*.md"))
    summary = (output_dir / "crawler_error_summary.md").read_text(encoding="utf-8")

    assert len(detail_files) == 2
    assert "Unique crawl jobs | 2" in summary
    assert "Total failed-page observations | 6" in summary
    assert "CRW_PERMANENT" in summary
    assert "HTTP_500" in summary


def test_export_crawler_error_report_records_supplemental_url_finding(tmp_path):
    output_dir = tmp_path / "reports"
    finding = {
        "tool_name": "diagnose_url_404_mismatch",
        "answer": "The current document URL returns HTTP 200, but the crawler URL resolves to 404.",
        "classification": "CRAWLER_URL_VERSION_MISMATCH",
        "evidence": [{"crawler_url": "https://docs.example.test/docs/utils.html", "upstream_status_code": 404}],
        "metrics": {
            "job_id": "job-report",
            "source_url": "https://docs.example.test/docs/main",
            "relative_resolution_without_slash": "https://docs.example.test/docs/utils.html",
            "relative_resolution_with_slash": "https://docs.example.test/docs/main/utils.html",
            "relative_link_root_cause": "SOURCE_URL_MISSING_TRAILING_SLASH",
            "mismatch_count": 1,
        },
        "recommended_actions": ["Add a trailing slash to the source URL."],
    }

    result = export_crawler_error_report(
        FakeReportClient(),
        "job-report",
        output_dir=output_dir,
        diagnostic_findings=[finding],
    )
    summary = (output_dir / "crawler_error_summary.md").read_text(encoding="utf-8")

    assert result.metrics["diagnostic_detail_report_paths"]
    assert "Additional QA findings" in summary
    assert "SOURCE_URL_MISSING_TRAILING_SLASH" in summary
    assert "Giải thích" in summary
    assert "Ảnh hưởng" in summary
    additional_section = summary.split("## Additional QA findings", 1)[1].split("## Crawl runs", 1)[0]
    assert "Occurrences" not in additional_section
    assert "Failed pages" not in additional_section
    detail_path = output_dir / result.metrics["diagnostic_detail_report_paths"][0]
    detail = detail_path.read_text(encoding="utf-8")
    assert "https://docs.example.test/docs/main" in detail
    assert "relative_resolution_without_slash" in detail

    export_crawler_error_report(FakeReportClient(), "job-report", output_dir=output_dir)
    summary_after_followup = (output_dir / "crawler_error_summary.md").read_text(encoding="utf-8")
    assert "SOURCE_URL_MISSING_TRAILING_SLASH" in summary_after_followup


def test_export_crawler_error_report_records_scope_leak_in_natural_language(tmp_path):
    output_dir = tmp_path / "reports"
    finding = {
        "tool_name": "diagnose_out_of_scope_urls",
        "answer": "Foody produced external Microsoft and X/Twitter URLs.",
        "classification": "OUT_OF_SCOPE_URL_LEAK",
        "evidence": [
            {"url": "https://answers.microsoft.com/en-us/media/logo.png", "kind": "RESOURCE", "content_type": "text/html"},
            {"url": "https://abs.twimg.com/favicons/twitter.3.ico", "kind": "NAVIGATION", "content_type": "image/vnd.microsoft.icon"},
        ],
        "metrics": {
            "job_id": "job-report",
            "scope_domains": ["foody.vn"],
            "out_of_scope_page_count": 12,
            "out_of_scope_link_count": 25,
            "html_resource_with_links_count": 8,
            "asset_url_returning_html_count": 8,
            "kind_mime_mismatch_count": 1,
            "finding_code": "OUT_OF_SCOPE_URL_LEAK",
        },
        "recommended_actions": ["Enforce the navigation host allowlist."],
    }

    export_crawler_error_report(
        FakeReportClient(),
        "job-report",
        output_dir=output_dir,
        diagnostic_findings=[finding],
    )
    summary = (output_dir / "crawler_error_summary.md").read_text(encoding="utf-8")

    assert "OUT_OF_SCOPE_URL_LEAK" in summary
    assert "resource URL trả về HTML" in summary
    assert "navigation allowlist" in summary
