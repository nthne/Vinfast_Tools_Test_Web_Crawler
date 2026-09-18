import httpx

from crawler_client.discovery import CrawlerDiscovery


def test_discovery_records_status_json_keys_and_pagination_shape():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/sources"):
            return httpx.Response(
                200,
                json={"data": {"items": [{"id": "s-1"}], "total": 1, "page": 1, "page_size": 50}, "status": "success"},
                request=request,
            )
        return httpx.Response(404, json={"detail": "Not found"}, request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url="https://crawler.test")
    endpoints = CrawlerDiscovery(client, candidates=["/api/v1.0/crawl/sources", "/api/v1.0/crawl/pages"]).probe()

    assert endpoints[0].status_code == 200
    assert endpoints[0].json_keys == ["items", "page", "page_size", "total"]
    assert endpoints[0].pagination == "items/page/page_size/total"
    assert endpoints[1].status_code == 404
    assert "Authorization" not in endpoints[0].to_dict()
