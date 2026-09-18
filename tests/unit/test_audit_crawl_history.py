from __future__ import annotations

from crawler_client.schemas import CrawledPage
from agent_tools.audit_crawl_history.tool import audit_crawl_history


class HistoryClient:
    def __init__(self):
        self.sources = [
            {"id": "source-foody", "name": "Foody", "domain": "foody.vn"},
            {"id": "source-pytorch", "name": "Pytorch", "domain": "pytorch.org"},
        ]
        self.jobs = {
            "job-foody": {
                "id": "job-foody",
                "source_id": "source-foody",
                "status": "COMPLETED",
                "started_at": "2026-09-16T07:00:00Z",
                "crawl_config": {"max_pages": 10, "max_resources": 20},
                "metadata": {"total_pages": 30, "in_queue_count": 0, "failed_count": 1},
            },
            "job-pytorch": {
                "id": "job-pytorch",
                "source_id": "source-pytorch",
                "status": "COMPLETED",
                "started_at": "2026-09-17T10:00:00Z",
                "crawl_config": {"max_pages": 10, "max_resources": 20},
                "metadata": {"total_pages": 2, "in_queue_count": 0, "failed_count": 1},
            },
        }
        self.pages = {
            "job-foody": [
                CrawledPage(
                    page_id="f1",
                    source_id="source-foody",
                    job_id="job-foody",
                    url="https://example.test/a/a/a/a",
                    metadata={
                        "status": "FAILED",
                        "kind": "RESOURCE",
                        "failure": {"code": "NO_PROXY_AVAILABLE", "retryable": False},
                        "error": {"code": "NO_PROXY_AVAILABLE", "message": "HTTP_403"},
                    },
                )
            ],
            "job-pytorch": [
                CrawledPage(
                    page_id="p1",
                    source_id="source-pytorch",
                    job_id="job-pytorch",
                    url="https://docs.example.test/docs/a.html",
                    metadata={
                        "status": "FAILED",
                        "kind": "NAVIGATION",
                        "failure": {"code": "CRW_PERMANENT", "retryable": False},
                        "error": {"code": "CRW_PERMANENT", "message": "CDP Target.createTarget: WS closed"},
                    },
                )
            ],
        }

    def list_sources(self):
        return self.sources

    def list_jobs(self, source_id=None, limit=None):
        values = [job for job in self.jobs.values() if source_id is None or job["source_id"] == source_id]
        return values[:limit] if limit is not None else values

    def get_job(self, job_id):
        return self.jobs[job_id]

    def list_pages(self, job_id=None, limit=None, source_id=None):
        pages = self.pages[job_id]
        return pages[:limit] if limit is not None else pages


def test_audit_crawl_history_writes_natural_language_reasons(tmp_path):
    output_path = tmp_path / "history-audit.md"

    result = audit_crawl_history(
        HistoryClient(),
        source_keywords=["foody", "pytorch"],
        start_date="2026-09-16",
        end_date="2026-09-17",
        output_path=output_path,
    )
    report = output_path.read_text(encoding="utf-8")

    assert result.tool_name == "audit_crawl_history"
    assert result.metrics["job_count"] == 2
    assert "Renderer/CDP" in report
    assert "proxy/403" in report
    assert "Lý do" in report
    assert "job-foody" in report
    assert "job-pytorch" in report
