from datetime import datetime

from crawler_client.mapper import CrawlerPageMapper


def test_mapper_reads_nested_metadata_and_preserves_upstream_fields():
    record = {
        "page_id": "p-1",
        "crawl_job_id": "job-1",
        "source_id": "source-1",
        "source_name": "Demo source",
        "url": "https://example.test/article",
        "domain": "example.test",
        "status": "NEW_INFO",
        "kind": "CONTENT",
        "content_type": None,
        "metadata": {
            "status_code": 200,
            "final_url": "https://example.test/article/",
            "title": "Demo article",
            "links": ["https://example.test/next"],
        },
        "created_at": "2026-08-07T08:50:15.210581+00:00",
        "content": "This is a useful article with enough words to inspect.",
        "depth": 2,
    }

    page = CrawlerPageMapper.map_record(record)

    assert page.page_id == "p-1"
    assert page.job_id == "job-1"
    assert page.status_code == 200
    assert page.final_url.endswith("/")
    assert page.title == "Demo article"
    assert page.markdown.startswith("This is a useful")
    assert page.extracted_text == page.markdown
    assert page.metadata["domain"] == "example.test"
    assert page.metadata["links"] == ["https://example.test/next"]
    assert isinstance(page.crawled_at, datetime)


def test_mapper_accepts_metadata_json_string_and_missing_optional_fields():
    page = CrawlerPageMapper.map_record(
        {
            "page_id": "p-2",
            "source_id": "source-1",
            "url": "https://example.test/missing",
            "metadata": '{"status_code": 404, "title": "Missing"}',
            "content": None,
        }
    )

    assert page.status_code == 404
    assert page.title == "Missing"
    assert page.final_url is None
    assert page.job_id is None
    assert page.text_for_qa == ""


def test_mapper_treats_float_nan_as_missing_text():
    page = CrawlerPageMapper.map_record(
        {
            "page_id": "p-3",
            "source_id": "source-1",
            "url": "https://example.test/nan",
            "content_type": float("nan"),
        }
    )

    assert page.content_type is None


def test_mapper_preserves_failure_and_retry_fields_for_diagnostics():
    page = CrawlerPageMapper.map_record(
        {
            "page_id": "p-4",
            "source_id": "source-1",
            "url": "https://example.test/failed",
            "status": "FAILED",
            "retry_count": 0,
            "failure": {
                "code": "CRW_PERMANENT",
                "category": "INTERNAL",
                "retryable": False,
            },
            "degraded": [],
        }
    )

    assert page.metadata["failure"]["code"] == "CRW_PERMANENT"
    assert page.metadata["retry_count"] == 0
