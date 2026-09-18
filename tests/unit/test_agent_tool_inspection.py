from __future__ import annotations

from types import SimpleNamespace

from agent_tools.analyze_resource_mix import analyze_resource_mix
from agent_tools.explain_page_classification import explain_page_classification
from agent_tools.inspect_job import inspect_job
from agent_tools.inspect_page import inspect_page
from agent_tools.inspect_source import inspect_source
from crawler_client.schemas import CrawledPage


class FakeInspectionClient:
    def __init__(self):
        self.pages = [
            CrawledPage(
                page_id="p-1",
                source_id="s-1",
                job_id="j-1",
                url="https://example.test/image.png",
                content_type="text/html",
                markdown="redirected html",
                metadata={
                    "kind": "RESOURCE",
                    "content_route": "HTML_MARKDOWN",
                    "final_url": "https://example.test/",
                    "warnings": ["redirected_to: https://example.test/"],
                    "depth": 2,
                },
            ),
            CrawledPage(
                page_id="p-2",
                source_id="s-1",
                job_id="j-1",
                url="https://example.test/about",
                content_type="text/html",
                markdown="about",
                metadata={"kind": "NAVIGATION", "content_route": "HTML_MARKDOWN", "depth": 1},
            ),
            CrawledPage(
                page_id="p-3",
                source_id="s-1",
                job_id="j-1",
                url="https://cdn.example.test/icon.svg",
                content_type="image/svg+xml",
                metadata={"kind": "RESOURCE", "content_route": "IMAGE", "depth": 2},
            ),
        ]

    def get_source(self, source_id):
        return {
            "id": source_id,
            "display_name": "Example",
            "url": "https://example.test",
            "domain": "example.test",
            "enabled": True,
            "crawl_config": {"max_pages": 100, "max_resources": 20},
            "rules": {"rules_filter_url": []},
            "degraded": [],
        }

    def get_job(self, job_id):
        return {
            "id": job_id,
            "source_id": "s-1",
            "status": "RUNNING",
            "crawl_config": {"max_pages": 100, "max_resources": 20},
            "metadata": {"total_pages": 3, "in_queue_count": 0, "success_count": 3, "failed_count": 0, "skipped_count": 0},
        }

    def list_pages(self, source_id=None, limit=None, job_id=None):
        pages = [p for p in self.pages if (source_id is None or p.source_id == source_id) and (job_id is None or p.job_id == job_id)]
        return pages[:limit] if limit is not None else pages

    def get_page(self, page_id):
        return next(page for page in self.pages if page.page_id == page_id)

    def get_page_view(self, page_id):
        page = self.get_page(page_id)
        return {"crawl_page_id": page_id, "url": page.url, "content_type": page.content_type, "markdown": page.markdown}


def test_inspect_source_returns_configuration_evidence():
    result = inspect_source(FakeInspectionClient(), "s-1")

    assert result.tool_name == "inspect_source"
    assert result.metrics["max_pages"] == 100
    assert any(item["field"] == "enabled" for item in result.evidence)


def test_inspect_job_calculates_effective_budget():
    result = inspect_job(FakeInspectionClient(), "j-1")

    assert result.metrics["effective_record_budget"] == 120
    assert result.metrics["total_pages"] == 3


def test_inspect_page_reports_content_lengths_without_full_content():
    result = inspect_page(FakeInspectionClient(), "p-1")

    assert result.metrics["kind"] == "RESOURCE"
    assert result.metrics["content_type"] == "text/html"
    assert result.metrics["markdown_characters"] == len("redirected html")
    assert "redirected html" not in result.to_dict()["answer"]


def test_analyze_resource_mix_flags_html_resource_and_external_host():
    result = analyze_resource_mix(FakeInspectionClient(), "j-1", sample_pages=10)

    assert result.metrics["resource_count"] == 2
    assert result.metrics["image_count"] == 1
    assert result.metrics["html_resource_count"] == 1
    assert result.metrics["external_resource_count"] == 1
    assert "RESOURCE_URL_RETURNS_HTML" in result.warnings


def test_explain_page_classification_separates_kind_from_response_mime():
    result = explain_page_classification(FakeInspectionClient(), "p-1")

    assert result.metrics["kind"] == "RESOURCE"
    assert result.metrics["content_type"] == "text/html"
    assert "RESOURCE_URL_RETURNS_HTML" in result.metrics["signals"]
    assert result.confidence == "observed"
