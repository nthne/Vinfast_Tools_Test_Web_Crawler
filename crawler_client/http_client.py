"""Authenticated, read-only HTTP client for the observed crawler API."""

from __future__ import annotations

import time
from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Any

import httpx

from auth.base import AuthProvider

from .mapper import CrawlerPageMapper
from .pagination import extract_items
from .schemas import CrawledPage

if TYPE_CHECKING:
    from config import AppSettings


class CrawlerAPIError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _unwrap(payload: Any) -> Any:
    if isinstance(payload, Mapping) and "data" in payload:
        return payload["data"]
    return payload


class HttpCrawlerClient:
    """Adapter for the FastAPI crawler endpoints discovered from OpenAPI."""

    DEFAULT_SOURCES_PATH = "/api/v1.0/crawl/sources"
    DEFAULT_JOBS_PATH = "/api/v1.0/crawl/jobs"
    DEFAULT_PAGES_PATH = "/api/v1.0/crawl/pages"
    DEFAULT_PAGE_DETAIL_PATH = "/api/v1.0/crawl/pages/{page_id}"
    DEFAULT_PAGE_VIEW_PATH = "/api/v1.0/crawl/pages/{page_id}/view"
    DEFAULT_PAGE_CLEAN_PREVIEW_PATH = "/api/v1.0/crawl/pages/{page_id}/clean-preview"
    DEFAULT_CLEAN_MODES_PATH = "/api/v1.0/crawl/exports/clean-modes"
    DEFAULT_EXPORTS_PATH = "/api/v1.0/crawl/exports"
    RETRYABLE_STATUS = {408, 429, 502, 503, 504}

    def __init__(
        self,
        base_url: str,
        auth_provider: AuthProvider | None = None,
        http_client: httpx.Client | None = None,
        *,
        sources_path: str | None = None,
        jobs_path: str | None = None,
        pages_path: str | None = None,
        page_detail_path: str | None = None,
        page_view_path: str | None = None,
        page_clean_preview_path: str | None = None,
        clean_modes_path: str | None = None,
        exports_path: str | None = None,
        request_timeout: float = 30.0,
        retry_count: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.http = http_client or httpx.Client(
            base_url=self.base_url,
            timeout=request_timeout,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        self.auth_provider = auth_provider
        self.retry_count = max(0, retry_count)
        self.sources_path = sources_path or self.DEFAULT_SOURCES_PATH
        self.jobs_path = jobs_path or self.DEFAULT_JOBS_PATH
        self.pages_path = pages_path or self.DEFAULT_PAGES_PATH
        self.page_detail_path = page_detail_path or self.DEFAULT_PAGE_DETAIL_PATH
        self.page_view_path = page_view_path or self.DEFAULT_PAGE_VIEW_PATH
        self.page_clean_preview_path = page_clean_preview_path or self.DEFAULT_PAGE_CLEAN_PREVIEW_PATH
        self.clean_modes_path = clean_modes_path or self.DEFAULT_CLEAN_MODES_PATH
        self.exports_path = exports_path or self.DEFAULT_EXPORTS_PATH
        self._auth_applied = False
        self._job_source_cache: dict[str, str] = {}
        if self.auth_provider is not None:
            self.authenticate()

    @classmethod
    def from_settings(cls, settings: AppSettings) -> "HttpCrawlerClient":
        from auth import provider_from_settings

        if not settings.base_url:
            raise CrawlerAPIError("CRAWLER_BASE_URL is required for HTTP access")
        return cls(
            settings.base_url,
            auth_provider=provider_from_settings(settings),
            sources_path=settings.sources_path,
            jobs_path=settings.jobs_path,
            pages_path=settings.pages_path,
            page_detail_path=settings.page_detail_path,
            page_view_path=settings.page_view_path,
            page_clean_preview_path=settings.page_clean_preview_path,
            clean_modes_path=settings.clean_modes_path,
            exports_path=settings.exports_path,
            request_timeout=settings.request_timeout,
            retry_count=settings.retry_count,
        )

    def authenticate(self) -> None:
        if self.auth_provider is not None and not self._auth_applied:
            self.auth_provider.authenticate(self.http)
            self._auth_applied = True

    def _request_json(self, path: str, params: Mapping[str, Any] | None = None) -> Any:
        self.authenticate()
        last_error: Exception | None = None
        for attempt in range(self.retry_count + 1):
            try:
                response = self.http.get(path, params=dict(params or {}))
                if response.status_code in self.RETRYABLE_STATUS and attempt < self.retry_count:
                    time.sleep(min(2.0, 0.2 * (2**attempt)))
                    continue
                if response.status_code < 200 or response.status_code >= 300:
                    message = f"Crawler API returned HTTP {response.status_code}"
                    try:
                        body = response.json()
                        if isinstance(body, dict):
                            detail = body.get("detail") or body.get("message") or body.get("error")
                            if detail:
                                message += f": {detail}"
                    except ValueError:
                        pass
                    raise CrawlerAPIError(message, response.status_code)
                try:
                    return response.json()
                except ValueError as exc:
                    raise CrawlerAPIError("UPSTREAM_SCHEMA_CHANGED: response was not JSON", response.status_code) from exc
            except CrawlerAPIError:
                raise
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt >= self.retry_count:
                    raise CrawlerAPIError(f"Crawler API request failed: {exc.__class__.__name__}") from exc
                time.sleep(min(2.0, 0.2 * (2**attempt)))
        raise CrawlerAPIError("Crawler API request failed") from last_error

    def _iter_items(self, path: str, params: Mapping[str, Any] | None = None, limit: int | None = None) -> Iterator[dict[str, Any]]:
        base = dict(params or {})
        page = int(base.pop("page", 1))
        page_size = min(limit, 100) if limit else 100
        yielded = 0
        while True:
            payload = _unwrap(self._request_json(path, {**base, "page": page, "page_size": page_size}))
            items, meta = extract_items(payload)
            if not items:
                return
            for item in items:
                yield item
                yielded += 1
                if limit is not None and yielded >= limit:
                    return
            total = meta.get("total")
            if isinstance(total, int) and page * page_size >= total:
                return
            page += 1

    def list_sources(self) -> list[dict[str, Any]]:
        sources = []
        for item in self._iter_items(self.sources_path):
            sources.append(
                {
                    "id": str(item.get("id") or item.get("source_id") or ""),
                    "name": item.get("display_name") or item.get("name") or item.get("url") or "",
                    "domain": item.get("domain"),
                    "page_count": item.get("page_count"),
                }
            )
        return sources

    def get_source(self, source_id: str) -> dict[str, Any]:
        payload = _unwrap(self._request_json(f"{self.sources_path}/{source_id}"))
        if not isinstance(payload, Mapping):
            raise CrawlerAPIError("UPSTREAM_SCHEMA_CHANGED: source detail is not an object")
        return dict(payload)

    def get_job(self, job_id: str) -> dict[str, Any]:
        payload = _unwrap(self._request_json(f"{self.jobs_path}/{job_id}"))
        if not isinstance(payload, Mapping):
            raise CrawlerAPIError("UPSTREAM_SCHEMA_CHANGED: job detail is not an object")
        return dict(payload)

    def list_jobs(self, source_id: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        params = {"source_id": source_id} if source_id else {}
        jobs = list(self._iter_items(self.jobs_path, params, limit))
        for job in jobs:
            if job.get("id") and job.get("source_id"):
                self._job_source_cache[str(job["id"])] = str(job["source_id"])
        return jobs

    def _source_for_job(self, job_id: str) -> str | None:
        if job_id in self._job_source_cache:
            return self._job_source_cache[job_id]
        payload = _unwrap(self._request_json(f"{self.jobs_path}/{job_id}"))
        if isinstance(payload, Mapping) and payload.get("source_id"):
            source_id = str(payload["source_id"])
            self._job_source_cache[job_id] = source_id
            return source_id
        return None

    def list_pages(
        self,
        source_id: str | None = None,
        limit: int | None = None,
        job_id: str | None = None,
    ) -> list[CrawledPage]:
        if source_id and not job_id:
            pages: list[CrawledPage] = []
            for job in self.list_jobs(source_id=source_id):
                current_job = str(job.get("id") or "")
                if not current_job:
                    continue
                remaining = None if limit is None else max(0, limit - len(pages))
                pages.extend(self.list_pages(source_id=source_id, limit=remaining, job_id=current_job))
                if limit is not None and len(pages) >= limit:
                    break
            return pages[:limit] if limit is not None else pages
        params: dict[str, Any] = {}
        if job_id:
            params["job_id"] = job_id
        if source_id and not job_id:
            # The observed API filters page rows by job_id, not source_id.
            params["source_id"] = source_id
        mapped: list[CrawledPage] = []
        for item in self._iter_items(self.pages_path, params, limit):
            raw = dict(item)
            inferred_source = source_id or raw.get("source_id")
            if not inferred_source and raw.get("crawl_job_id"):
                inferred_source = self._source_for_job(str(raw["crawl_job_id"]))
            if inferred_source:
                raw["source_id"] = inferred_source
            try:
                mapped.append(CrawlerPageMapper.map_record(raw))
            except ValueError as exc:
                raise CrawlerAPIError(str(exc)) from exc
        return mapped

    def get_page(self, page_id: str) -> CrawledPage:
        payload = _unwrap(self._request_json(self.page_detail_path.format(page_id=page_id)))
        if not isinstance(payload, Mapping):
            raise CrawlerAPIError("UPSTREAM_SCHEMA_CHANGED: page detail is not an object")
        raw = dict(payload)
        inferred_source = raw.get("source_id")
        if not inferred_source and raw.get("crawl_job_id"):
            inferred_source = self._source_for_job(str(raw["crawl_job_id"]))
        if inferred_source:
            raw["source_id"] = inferred_source
        try:
            try:
                view = _unwrap(self._request_json(self.page_view_path.format(page_id=page_id)))
            except CrawlerAPIError as exc:
                if exc.status_code not in {403, 404}:
                    raise
                view = None
            if isinstance(view, Mapping):
                for key in ("markdown", "content_type", "download_url"):
                    if view.get(key) is not None:
                        raw[key] = view[key]
                if view.get("markdown") is not None and not raw.get("extracted_text"):
                    raw["extracted_text"] = view["markdown"]
            return CrawlerPageMapper.map_record(raw)
        except ValueError as exc:
            raise CrawlerAPIError(str(exc)) from exc

    def get_page_view(self, page_id: str) -> dict[str, Any]:
        payload = _unwrap(self._request_json(self.page_view_path.format(page_id=page_id)))
        if not isinstance(payload, Mapping):
            raise CrawlerAPIError("UPSTREAM_SCHEMA_CHANGED: page view is not an object")
        return dict(payload)

    def list_clean_modes(self) -> dict[str, Any]:
        payload = _unwrap(self._request_json(self.clean_modes_path))
        if not isinstance(payload, Mapping):
            raise CrawlerAPIError("UPSTREAM_SCHEMA_CHANGED: clean modes are not an object")
        return dict(payload)

    def preview_clean(self, page_id: str, clean_mode: str, scope: str = "PAGE") -> dict[str, Any]:
        payload = _unwrap(
            self._request_json(
                self.page_clean_preview_path.format(page_id=page_id),
                {"clean_mode": clean_mode, "scope": scope},
            )
        )
        if not isinstance(payload, Mapping):
            raise CrawlerAPIError("UPSTREAM_SCHEMA_CHANGED: clean preview is not an object")
        return dict(payload)

    def list_exports(self, limit: int | None = None) -> list[dict[str, Any]]:
        return list(self._iter_items(self.exports_path, limit=limit))
