import csv
import json

from crawler_client.file_client import FileCrawlerClient


def test_file_client_lists_sources_and_filters_pages(tmp_path):
    path = tmp_path / "crawl.csv"
    rows = [
        {
            "page_id": "p-1",
            "source_id": "s-1",
            "source_name": "One",
            "url": "https://one.test/a",
            "metadata": json.dumps({"status_code": 200}),
            "content": "alpha",
        },
        {
            "page_id": "p-2",
            "source_id": "s-2",
            "source_name": "Two",
            "url": "https://two.test/b",
            "metadata": json.dumps({"status_code": 200}),
            "content": "beta",
        },
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)

    client = FileCrawlerClient(path)

    assert client.list_sources() == [
        {"id": "s-1", "name": "One", "page_count": 1},
        {"id": "s-2", "name": "Two", "page_count": 1},
    ]
    assert [page.page_id for page in client.list_pages("s-2")] == ["p-2"]
    assert client.get_page("p-1").url == "https://one.test/a"


def test_file_client_derives_completed_job_summary_from_export(tmp_path):
    path = tmp_path / "crawl.json"
    path.write_text(
        json.dumps(
            [
                {
                    "page_id": "p-1",
                    "source_id": "s-1",
                    "crawl_job_id": "job-1",
                    "url": "https://one.test/a",
                    "status": "NEW_INFO",
                },
                {
                    "page_id": "p-2",
                    "source_id": "s-1",
                    "crawl_job_id": "job-1",
                    "url": "https://one.test/b",
                    "status": "FAILED",
                },
            ]
        ),
        encoding="utf-8",
    )

    job = FileCrawlerClient(path).get_job("job-1")

    assert job["status"] == "COMPLETED"
    assert job["metadata"]["total_pages"] == 2
    assert job["metadata"]["failed_count"] == 1
