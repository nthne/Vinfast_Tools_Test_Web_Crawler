from crawler_client.schemas import CrawledPage

from agent_tools.diagnose_out_of_scope_urls import diagnose_out_of_scope_urls


class ScopeLeakClient:
    def __init__(self):
        self.pages = [
            CrawledPage(
                page_id="p-1",
                source_id="s-1",
                job_id="j-1",
                url="https://www.foody.vn/ha-noi",
                content_type="text/html",
                metadata={
                    "kind": "NAVIGATION",
                    "depth": 1,
                    "links": [
                        "https://go.microsoft.com/fwlink/p?LinkID=2092881",
                        "https://support.microsoft.com/en-us/teams",
                        "https://abs.twimg.com/favicons/twitter.3.ico",
                    ],
                },
            ),
            CrawledPage(
                page_id="p-2",
                source_id="s-1",
                job_id="j-1",
                url="https://x.com/apple-touch-icon.png",
                content_type="text/html",
                metadata={
                    "kind": "RESOURCE",
                    "depth": 2,
                    "warnings": ["redirected_to: https://x.com/apple-touch-icon.png"],
                    "links": ["https://abs.twimg.com/favicons/twitter.3.ico"],
                },
            ),
            CrawledPage(
                page_id="p-3",
                source_id="s-1",
                job_id="j-1",
                url="https://abs.twimg.com/favicons/twitter.3.ico",
                content_type="image/vnd.microsoft.icon",
                metadata={"kind": "NAVIGATION", "depth": 3},
            ),
        ]

    def get_job(self, job_id):
        return {"id": job_id, "source_id": "s-1", "status": "COMPLETED", "metadata": {"total_pages": 3}}

    def get_source(self, source_id):
        return {"id": source_id, "url": "https://www.foody.vn/ha-noi", "domain": "foody.vn"}

    def list_pages(self, job_id=None, limit=None):
        pages = [page for page in self.pages if page.job_id == job_id]
        return pages[:limit] if limit is not None else pages


def test_diagnose_out_of_scope_urls_explains_html_resource_following_and_scope_leak():
    result = diagnose_out_of_scope_urls(ScopeLeakClient(), "j-1")

    assert result.classification == "OUT_OF_SCOPE_URL_LEAK"
    assert result.metrics["out_of_scope_page_count"] == 2
    assert result.metrics["out_of_scope_link_count"] == 3
    assert result.metrics["html_resource_with_links_count"] == 1
    assert result.metrics["kind_mime_mismatch_count"] == 1
    assert "RESOURCE_HTML_LINK_FOLLOWING" in result.warnings
    assert "SOURCE_SCOPE_NOT_ENFORCED" in result.warnings
    assert any("go.microsoft.com/fwlink" in str(item) for item in result.evidence)
