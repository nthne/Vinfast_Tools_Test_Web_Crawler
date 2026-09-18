from __future__ import annotations

from agent_tools.diagnose_failed_pages import diagnose_failed_pages
from crawler_client.schemas import CrawledPage


class FakeFailureClient:
    def __init__(self):
        self.job = {
            "id": "job-pytorch",
            "source_id": "source-pytorch",
            "status": "COMPLETED",
            "crawl_config": {"render_js": None, "max_pages": 100, "max_resources": 200},
            "metadata": {"total_pages": 5, "failed_count": 4, "success_count": 1},
        }
        self.pages = [
            CrawledPage(
                page_id=f"failed-{index}",
                source_id="source-pytorch",
                job_id="job-pytorch",
                url=f"https://docs.example.test/page-{index}",
                metadata={
                    "status": "FAILED",
                    "kind": "NAVIGATION",
                    "error": {
                        "code": "CRW_PERMANENT",
                        "message": "js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed",
                        "retryable": False,
                    },
                    "failure": {
                        "category": "INTERNAL",
                        "http_status": None,
                        "retryable": False,
                    },
                },
            )
            for index in range(4)
        ] + [
            CrawledPage(
                page_id="success-1",
                source_id="source-pytorch",
                job_id="job-pytorch",
                url="https://docs.example.test/ok",
                status_code=200,
                content_type="text/html",
                metadata={"status": "NEW_INFO", "kind": "NAVIGATION"},
            )
        ]

    def get_job(self, job_id):
        return self.job

    def list_pages(self, job_id=None, limit=None):
        return self.pages[:limit] if limit is not None else self.pages


def test_diagnose_failed_pages_identifies_renderer_infrastructure_failure():
    result = diagnose_failed_pages(FakeFailureClient(), "job-pytorch")

    assert result.classification == "RENDERER_INFRASTRUCTURE_FAILURE"
    assert result.metrics["failed_count"] == 4
    assert result.metrics["dominant_error_code"] == "CRW_PERMANENT"
    assert result.metrics["no_http_response_count"] == 4
    assert result.metrics["renderer_error_count"] == 4
    assert "JS_ESCALATION_FAILURE" in result.warnings
    assert "NO_HTTP_RESPONSE_RECORDED" in result.warnings
