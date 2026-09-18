from __future__ import annotations

from crawler_client.schemas import CrawledPage
from agent_tools.diagnose_url_404_mismatch.tool import diagnose_url_404_mismatch


def test_detects_versioned_upstream_url_when_crawler_keeps_404_path():
    pages = [
        CrawledPage(
            page_id="old-utils",
            source_id="source-1",
            job_id="job-1",
            url="https://docs.pytorch.org/docs/utils.html",
            status_code=404,
            metadata={"status": "SUCCESS", "kind": "NAVIGATION"},
        )
    ]

    class Client:
        def list_pages(self, **kwargs):
            return pages

    def probe(url: str, timeout: float) -> dict:
        if url.endswith("/docs/2.14/utils.html"):
            return {"status_code": 200, "final_url": url, "content_type": "text/html"}
        return {"status_code": 404, "final_url": url, "content_type": "text/html"}

    result = diagnose_url_404_mismatch(
        Client(),
        job_id="job-1",
        expected_url="https://docs.pytorch.org/docs/2.14/utils.html",
        probe_url=probe,
    )

    assert result.classification == "CRAWLER_URL_VERSION_MISMATCH"
    assert result.metrics["crawler_404_count"] == 1
    assert result.metrics["expected_status_code"] == 200
    assert result.evidence[0]["crawler_url"] == "https://docs.pytorch.org/docs/utils.html"


def test_distinguishes_real_upstream_404_from_current_url_success():
    pages = [
        CrawledPage(
            page_id="missing",
            source_id="source-1",
            job_id="job-1",
            url="https://docs.pytorch.org/docs/missing.html",
            status_code=404,
            metadata={"status": "SUCCESS", "kind": "NAVIGATION"},
        )
    ]

    class Client:
        def list_pages(self, **kwargs):
            return pages

    def probe(url: str, timeout: float) -> dict:
        return {"status_code": 404, "final_url": url, "content_type": "text/html"}

    result = diagnose_url_404_mismatch(
        Client(),
        job_id="job-1",
        expected_url="https://docs.pytorch.org/docs/missing.html",
        probe_url=probe,
    )

    assert result.classification == "UPSTREAM_404_CONFIRMED"
    assert result.metrics["expected_status_code"] == 404
    assert result.metrics["mismatch_count"] == 0


def test_explains_missing_trailing_slash_as_relative_link_root_cause():
    pages = [
        CrawledPage(
            page_id="old-utils",
            source_id="source-1",
            job_id="job-1",
            url="https://docs.pytorch.org/docs/utils.html",
            status_code=None,
            metadata={"status": "FAILED", "kind": "NAVIGATION"},
        )
    ]

    class Client:
        def list_pages(self, **kwargs):
            return pages

        def get_job(self, job_id):
            return {"id": job_id, "source_id": "source-1"}

        def get_source(self, source_id):
            return {"id": source_id, "url": "https://docs.pytorch.org/docs/main"}

    def probe(url: str, timeout: float) -> dict:
        return {"status_code": 200 if url.endswith("/docs/main/utils.html") else 404, "final_url": url}

    result = diagnose_url_404_mismatch(
        Client(),
        job_id="job-1",
        expected_url="https://docs.pytorch.org/docs/main/utils.html",
        probe_url=probe,
    )

    assert result.metrics["source_url"] == "https://docs.pytorch.org/docs/main"
    assert result.metrics["relative_resolution_without_slash"] == "https://docs.pytorch.org/docs/utils.html"
    assert result.metrics["relative_resolution_with_slash"] == "https://docs.pytorch.org/docs/main/utils.html"
    assert "SOURCE_URL_MISSING_TRAILING_SLASH" in result.warnings
