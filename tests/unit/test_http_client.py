import httpx

from auth.api_key import ApiKeyAuth
from crawler_client.http_client import HttpCrawlerClient


def test_http_client_uses_actual_api_paths_and_unwraps_pagination():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path == "/api/v1.0/crawl/sources":
            return httpx.Response(
                200,
                json={
                    "data": {
                        "items": [{"id": "s-1", "display_name": "Source 1", "domain": "example.test"}],
                        "total": 1,
                        "page": 1,
                        "page_size": 100,
                    },
                    "status": "success",
                },
                request=request,
            )
        if request.url.path == "/api/v1.0/crawl/pages":
            return httpx.Response(
                200,
                json={
                    "data": {
                        "items": [
                            {
                                "id": "p-1",
                                "source_id": "s-1",
                                "crawl_job_id": "job-1",
                                "url": "https://example.test/a",
                                "metadata": {"status_code": 200, "title": "A"},
                            }
                        ],
                        "total": 1,
                        "page": 1,
                        "page_size": 100,
                    },
                    "status": "success",
                },
                request=request,
            )
        return httpx.Response(404, json={"detail": "Not found"}, request=request)

    raw = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://crawler.test")
    client = HttpCrawlerClient(
        "https://crawler.test",
        auth_provider=ApiKeyAuth("api-key"),
        http_client=raw,
        retry_count=0,
    )

    assert client.list_sources() == [
        {"id": "s-1", "name": "Source 1", "domain": "example.test", "page_count": None}
    ]
    pages = client.list_pages(source_id="s-1", job_id="job-1")

    assert pages[0].page_id == "p-1"
    assert pages[0].title == "A"
    assert seen[0].headers["Authorization"] == "Bearer api-key"
    assert seen[1].url.params["job_id"] == "job-1"
    assert "source_id" not in seen[1].url.params


def test_http_client_merges_view_markdown_into_page_detail():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/view"):
            return httpx.Response(
                200,
                json={"data": {"crawl_page_id": "p-1", "url": "https://example.test/a", "markdown": "Body"}},
                request=request,
            )
        return httpx.Response(
            200,
            json={
                "data": {
                    "id": "p-1",
                    "source_id": "s-1",
                    "crawl_job_id": "job-1",
                    "url": "https://example.test/a",
                    "metadata": {"status_code": 200},
                },
                "status": "success",
            },
            request=request,
        )

    raw = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://crawler.test")
    page = HttpCrawlerClient(
        "https://crawler.test", auth_provider=ApiKeyAuth("key"), http_client=raw, retry_count=0
    ).get_page("p-1")

    assert page.markdown == "Body"
    assert page.extracted_text == "Body"


def test_http_client_exposes_read_only_job_view_clean_and_export_methods():
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path.endswith("/jobs/job-1"):
            return httpx.Response(200, json={"data": {"id": "job-1", "status": "RUNNING"}}, request=request)
        if request.url.path.endswith("/pages/p-1/view"):
            return httpx.Response(200, json={"data": {"crawl_page_id": "p-1", "markdown": "Body"}}, request=request)
        if request.url.path.endswith("/exports/clean-modes"):
            return httpx.Response(200, json={"data": {"items": [{"mode": "RAW"}]}}, request=request)
        if request.url.path.endswith("/pages/p-1/clean-preview"):
            return httpx.Response(
                200,
                json={"data": {"clean_mode": "SAFE", "scope": "PAGE", "original_characters": 10, "kept_characters": 9}},
                request=request,
            )
        if request.url.path.endswith("/exports"):
            return httpx.Response(
                200,
                json={"data": {"items": [{"id": "export-1", "status": "COMPLETED"}], "total": 1, "page": 1, "page_size": 100}},
                request=request,
            )
        return httpx.Response(404, json={"detail": "Not found"}, request=request)

    raw = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://crawler.test")
    client = HttpCrawlerClient("https://crawler.test", auth_provider=ApiKeyAuth("key"), http_client=raw, retry_count=0)

    assert client.get_job("job-1")["status"] == "RUNNING"
    assert client.get_page_view("p-1")["markdown"] == "Body"
    assert client.list_clean_modes()["items"][0]["mode"] == "RAW"
    assert client.preview_clean("p-1", "SAFE")["kept_characters"] == 9
    assert client.list_exports()[0]["id"] == "export-1"
    assert any(request.url.params.get("clean_mode") == "SAFE" for request in seen)
    assert any(request.url.params.get("scope") == "PAGE" for request in seen)
