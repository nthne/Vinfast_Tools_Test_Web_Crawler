"""Explain external URL leakage and resource/page scope confusion."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

from crawler_client.schemas import CrawledPage

from ..models import ToolResult


_ASSET_SUFFIXES = (
    ".avif",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".webp",
)


def _metadata(page: CrawledPage) -> dict[str, Any]:
    return page.metadata if isinstance(page.metadata, dict) else {}


def _host(url: str | None) -> str:
    try:
        return (urlsplit(str(url or "")).hostname or "").lower().rstrip(".")
    except ValueError:
        return ""


def _scope_domain(value: str | None) -> str:
    host = _host(value)
    return host[4:] if host.startswith("www.") else host


def _in_scope(host: str, allowed_domains: set[str]) -> bool:
    return bool(host) and any(host == domain or host.endswith(f".{domain}") for domain in allowed_domains if domain)


def _is_html(content_type: str | None) -> bool:
    return str(content_type or "").casefold().split(";", 1)[0].strip() == "text/html"


def _is_binary_navigation(kind: str, content_type: str | None) -> bool:
    return kind == "NAVIGATION" and str(content_type or "").casefold().startswith(("image/", "audio/", "video/", "application/pdf"))


def _is_asset_url(url: str) -> bool:
    path = urlsplit(url).path.casefold()
    return path.endswith(_ASSET_SUFFIXES)


def _warnings(metadata: Mapping[str, Any]) -> list[str]:
    value = metadata.get("warnings")
    return [str(item) for item in value] if isinstance(value, list) else []


def _links(metadata: Mapping[str, Any]) -> list[str]:
    value = metadata.get("links")
    return [str(item) for item in value if item] if isinstance(value, list) else []


def diagnose_out_of_scope_urls(client: Any, job_id: str, sample_pages: int | None = None) -> ToolResult:
    """Diagnose pages and links that escape a source's configured host scope.

    The check is read-only. It deliberately keeps page kind separate from response
    MIME: an image MIME on a NAVIGATION record is a classification mismatch, while
    an HTML response from a RESOURCE URL is evidence that resource HTML may have
    been parsed and followed as navigation.
    """

    job = client.get_job(job_id)
    source_id = str(job.get("source_id") or "")
    source = client.get_source(source_id) if source_id else {}
    pages = client.list_pages(job_id=job_id, limit=sample_pages)

    allowed_domains = {
        domain
        for domain in (
            _scope_domain(source.get("domain")),
            _scope_domain(source.get("url")),
        )
        if domain
    }
    scope_known = bool(allowed_domains)

    out_of_scope_pages: list[dict[str, Any]] = []
    out_of_scope_links: dict[str, dict[str, Any]] = {}
    external_domains: Counter[str] = Counter()
    external_link_domains: Counter[str] = Counter()
    kind_counts: Counter[str] = Counter()
    html_resource_with_links: list[dict[str, Any]] = []
    asset_html_pages: list[dict[str, Any]] = []
    kind_mime_mismatches: list[dict[str, Any]] = []
    expanded_pages: list[dict[str, Any]] = []

    for page in pages:
        metadata = _metadata(page)
        kind = str(metadata.get("kind") or "UNKNOWN").upper()
        page_host = _host(page.url)
        content_type = str(page.content_type or "UNKNOWN")
        links = _links(metadata)
        kind_counts[kind] += 1

        if scope_known and page_host and not _in_scope(page_host, allowed_domains):
            external_domains[page_host] += 1
            out_of_scope_pages.append(
                {
                    "page_id": page.page_id,
                    "url": page.url,
                    "host": page_host,
                    "kind": kind,
                    "content_type": content_type,
                    "depth": metadata.get("depth"),
                    "title": metadata.get("title"),
                    "final_url": metadata.get("final_url"),
                    "warnings": _warnings(metadata),
                }
            )

        if kind == "RESOURCE" and _is_html(page.content_type) and links:
            html_resource_with_links.append(
                {
                    "page_id": page.page_id,
                    "url": page.url,
                    "link_count": len(links),
                    "final_url": metadata.get("final_url"),
                    "warnings": _warnings(metadata),
                }
            )

        if kind == "RESOURCE" and _is_asset_url(page.url) and _is_html(page.content_type):
            asset_html_pages.append(
                {"page_id": page.page_id, "url": page.url, "content_type": content_type, "title": metadata.get("title")}
            )

        if _is_binary_navigation(kind, page.content_type):
            kind_mime_mismatches.append(
                {"page_id": page.page_id, "url": page.url, "kind": kind, "content_type": content_type}
            )

        path_parts = [part for part in urlsplit(page.url).path.split("/") if part]
        if len(path_parts) > 20 or any(path_parts.count(part) >= 3 for part in set(path_parts)):
            expanded_pages.append({"page_id": page.page_id, "url": page.url, "depth": metadata.get("depth")})

        for link in links:
            link_host = _host(link)
            if not link_host or not scope_known or _in_scope(link_host, allowed_domains):
                continue
            external_link_domains[link_host] += 1
            out_of_scope_links.setdefault(
                link,
                {
                    "target_url": link,
                    "target_host": link_host,
                    "source_page_id": page.page_id,
                    "source_url": page.url,
                    "source_kind": kind,
                    "source_content_type": content_type,
                    "source_title": metadata.get("title"),
                    "source_warnings": _warnings(metadata),
                },
            )

    warnings: list[str] = []
    if not scope_known:
        warnings.append("SOURCE_SCOPE_UNKNOWN")
    if out_of_scope_pages:
        warnings.append("SOURCE_SCOPE_NOT_ENFORCED")
    if any(item["kind"] == "NAVIGATION" for item in out_of_scope_pages):
        warnings.append("EXTERNAL_NAVIGATION_PAGES")
    if any(item["kind"] == "RESOURCE" for item in out_of_scope_pages):
        warnings.append("EXTERNAL_RESOURCE_PAGES")
    if html_resource_with_links:
        warnings.append("RESOURCE_HTML_LINK_FOLLOWING")
    if asset_html_pages:
        warnings.append("ASSET_URL_RETURNS_HTML")
    if kind_mime_mismatches:
        warnings.append("NAVIGATION_MIME_MISMATCH")
    if external_link_domains:
        warnings.append("EXTERNAL_LINKS_DISCOVERED")
    if expanded_pages:
        warnings.append("URL_PATH_EXPANSION")

    if not scope_known:
        classification = "INSUFFICIENT_SCOPE_DATA"
    elif out_of_scope_pages and html_resource_with_links:
        classification = "OUT_OF_SCOPE_URL_LEAK"
    elif out_of_scope_pages:
        classification = "EXTERNAL_SCOPE_LEAK"
    elif external_link_domains:
        classification = "EXTERNAL_LINKS_DISCOVERED"
    else:
        classification = "NO_SCOPE_LEAK_OBSERVED"

    if out_of_scope_pages or external_link_domains:
        answer = (
            f"Job {job_id} được phân loại {classification}: source scope={sorted(allowed_domains) or ['UNKNOWN']}; "
            f"quan sát {len(out_of_scope_pages)} page ngoài scope và {len(out_of_scope_links)} URL ngoài scope trong metadata.links."
        )
    else:
        answer = f"Job {job_id} không có URL ngoài scope trong dữ liệu đã kiểm tra."

    evidence = [
        {"field": "source_scope", "observed": sorted(allowed_domains)},
        {"field": "job_config", "observed": job.get("crawl_config") or {}},
        {"field": "page_kind_distribution", "observed": dict(kind_counts)},
        {"field": "out_of_scope_pages", "observed": out_of_scope_pages[:20]},
        {"field": "out_of_scope_links", "observed": list(out_of_scope_links.values())[:30]},
        {"field": "external_domain_distribution", "observed": dict(external_domains)},
        {"field": "external_link_domain_distribution", "observed": dict(external_link_domains)},
        {"field": "html_resources_with_links", "observed": html_resource_with_links[:20]},
        {"field": "asset_urls_returning_html", "observed": asset_html_pages[:20]},
        {"field": "navigation_mime_mismatches", "observed": kind_mime_mismatches[:20]},
        {"field": "url_path_expansion_samples", "observed": expanded_pages[:20]},
    ]

    return ToolResult(
        tool_name="diagnose_out_of_scope_urls",
        answer=answer,
        evidence=evidence,
        metrics={
            "job_id": job_id,
            "source_id": source_id,
            "sample_count": len(pages),
            "scope_domains": sorted(allowed_domains),
            "out_of_scope_page_count": len(out_of_scope_pages),
            "out_of_scope_link_count": len(out_of_scope_links),
            "out_of_scope_link_occurrence_count": sum(external_link_domains.values()),
            "external_navigation_page_count": sum(1 for item in out_of_scope_pages if item["kind"] == "NAVIGATION"),
            "external_resource_page_count": sum(1 for item in out_of_scope_pages if item["kind"] == "RESOURCE"),
            "html_resource_with_links_count": len(html_resource_with_links),
            "asset_url_returning_html_count": len(asset_html_pages),
            "kind_mime_mismatch_count": len(kind_mime_mismatches),
            "url_path_expansion_count": len(expanded_pages),
            "external_domains": dict(external_domains),
            "external_link_domains": dict(external_link_domains),
        },
        warnings=sorted(set(warnings)),
        recommended_actions=[
            "Enforce the source host allowlist before enqueueing NAVIGATION URLs; keep external asset hosts separate from navigation scope.",
            "Do not extract or enqueue hyperlinks from RESOURCE responses unless the resource was explicitly allowed to be HTML navigation.",
            "When an asset URL returns HTML or redirects, record the MIME/redirect mismatch and stop link expansion from that resource.",
            "Canonicalize URLs before enqueueing: resolve redirects, collapse repeated path segments, normalize escapes, and deduplicate query variants.",
            "Keep page and resource budgets separate; a resource must not consume page budget or become a page only because its MIME is text/html.",
        ],
        confidence="observed" if scope_known else "insufficient_data",
        classification=classification,
    )
