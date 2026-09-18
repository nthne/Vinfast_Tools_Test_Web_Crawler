from __future__ import annotations

from agent_tools.diagnose_crawl_stall import diagnose_crawl_stall
from crawler_client.schemas import CrawledPage


class FakeJobClient:
    def __init__(self):
        self.job = {
            "id": "j-1",
            "source_id": "s-1",
            "status": "RUNNING",
            "updated_at": "2026-09-18T01:00:00Z",
            "crawl_config": {"max_pages": 100, "max_resources": 200},
            "metadata": {"total_pages": 300, "in_queue_count": 20, "success_count": 200, "failed_count": 50, "skipped_count": 30},
        }
        self.pages = [
            CrawledPage(
                page_id="p-1",
                source_id="s-1",
                job_id="j-1",
                url="https://example.test/static/images/logo/static/images/logo/static/images/logo/a.png",
                metadata={"kind": "RESOURCE", "depth": 2},
            ),
            CrawledPage(
                page_id="p-2",
                source_id="s-1",
                job_id="j-1",
                url="https://example.test/a.png?x=1",
                metadata={"kind": "RESOURCE", "depth": 2},
            ),
            CrawledPage(
                page_id="p-3",
                source_id="s-1",
                job_id="j-1",
                url="https://example.test/a.png?x=2",
                metadata={"kind": "RESOURCE", "depth": 2},
            ),
        ]

    def get_job(self, job_id):
        return self.job

    def get_source(self, source_id):
        return {"id": source_id, "crawl_config": {"max_pages": 100, "max_resources": 100}}

    def list_pages(self, job_id=None, limit=None):
        return self.pages[:limit] if limit is not None else self.pages


def test_diagnose_crawl_stall_reports_budget_and_url_expansion_evidence():
    result = diagnose_crawl_stall(FakeJobClient(), "j-1", poll_seconds=0, sample_pages=(1,))

    assert result.metrics["effective_record_budget"] == 300
    assert result.metrics["runtime_source_resource_budget_delta"] == 100
    assert result.metrics["exact_duplicate_url_groups"] == 0
    assert result.metrics["url_path_expansion_count"] == 1
    assert "JOB_RUNTIME_CONFIG_DIFFERS_FROM_SOURCE" in result.warnings
    assert "URL_PATH_EXPANSION" in result.warnings
    assert result.classification == "URL_EXPANSION_SUSPECTED"


def test_diagnose_crawl_stall_marks_running_budget_with_queue_as_budget_exhausted():
    client = FakeJobClient()
    client.pages = []
    result = diagnose_crawl_stall(client, "j-1", poll_seconds=0, sample_pages=(1,))

    assert result.classification == "BUDGET_EXHAUSTED"
    assert "JOB_BUDGET_EXHAUSTED_NOT_TERMINATED" in result.warnings


def test_diagnose_crawl_stall_reports_unchanged_poll(monkeypatch):
    monkeypatch.setattr("agent_tools.diagnose_crawl_stall.tool.time.sleep", lambda _seconds: None)

    result = diagnose_crawl_stall(FakeJobClient(), "j-1", poll_seconds=1, sample_pages=(1,))

    assert result.classification == "STALLED"
    assert result.metrics["poll_stalled"] is True
