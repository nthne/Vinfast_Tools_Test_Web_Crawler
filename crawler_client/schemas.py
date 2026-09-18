"""Normalized crawler-facing schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class CrawledPage:
    page_id: str
    source_id: str
    url: str
    job_id: str | None = None
    final_url: str | None = None
    title: str | None = None
    status_code: int | None = None
    content_type: str | None = None
    response_time_ms: int | None = None
    raw_html: str | None = None
    raw_text: str | None = None
    extracted_text: str | None = None
    clean_text: str | None = None
    markdown: str | None = None
    language: str | None = None
    crawled_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def text_for_qa(self) -> str:
        """Return the best available semantic text for content checks."""

        for value in (self.extracted_text, self.clean_text, self.markdown, self.raw_text):
            if value is not None:
                return str(value)
        return ""

    @property
    def word_count(self) -> int:
        return len(self.text_for_qa.split())

    @property
    def char_count(self) -> int:
        return len(self.text_for_qa)
