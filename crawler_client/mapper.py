"""Map crawler-specific rows to the stable internal page schema."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .schemas import CrawledPage


def _first(record: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        value = record.get(name)
        if value is not None and value != "":
            return value
    return None


def _as_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return str(value)


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _metadata(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {"_raw_metadata": value}
        return dict(parsed) if isinstance(parsed, Mapping) else {"_metadata_value": parsed}
    return {}


class CrawlerPageMapper:
    """Normalize common crawler response variants without assuming one schema."""

    @staticmethod
    def map_record(record: Mapping[str, Any]) -> CrawledPage:
        nested = _metadata(record.get("metadata"))
        page_id = _first(record, "page_id", "id")
        source_id = _first(record, "source_id", "source", "sourceId")
        url = _first(record, "url", "requested_url", "request_url") or ""
        if page_id is None or source_id is None:
            raise ValueError("UPSTREAM_SCHEMA_CHANGED: page_id and source_id are required")

        def value(*names: str) -> Any:
            return _first(record, *names) or nested.get(names[0])

        raw_html = _as_text(_first(record, "raw_html", "html"))
        raw_text = _as_text(_first(record, "raw_text"))
        extracted = _as_text(_first(record, "extracted_text", "text"))
        clean = _as_text(_first(record, "clean_text", "cleaned_text"))
        markdown = _as_text(_first(record, "markdown"))
        content = _as_text(_first(record, "content", "body"))
        if content is not None and not any((raw_html, raw_text, extracted, clean, markdown)):
            markdown = content
            extracted = content

        metadata = dict(nested)
        for key in (
            "domain",
            "source_name",
            "status",
            "kind",
            "source_hash",
            "updated_at",
            "depth",
            "failure",
            "retry_count",
            "degraded",
            "ref_crawl_page_id",
            "proxy_id",
        ):
            if key in record and record[key] is not None:
                metadata.setdefault(key, record[key])

        return CrawledPage(
            page_id=str(page_id),
            source_id=str(source_id),
            job_id=_as_text(_first(record, "job_id", "crawl_job_id", "crawlJobId")),
            url=str(url),
            final_url=_as_text(value("final_url", "resolved_url")),
            title=_as_text(value("title", "page_title")),
            status_code=_as_int(value("status_code", "http_status", "statusCode")),
            content_type=_as_text(value("content_type", "mime_type", "contentType")),
            response_time_ms=_as_int(value("response_time_ms", "responseTimeMs")),
            raw_html=raw_html,
            raw_text=raw_text,
            extracted_text=extracted,
            clean_text=clean,
            markdown=markdown,
            language=_as_text(value("language", "lang")),
            crawled_at=_as_datetime(_first(record, "crawled_at", "created_at", "crawl_time")),
            metadata=metadata,
        )
