"""Read-only local export client for CSV, JSON, and Parquet."""

from __future__ import annotations

import csv
import json
from collections import Counter, OrderedDict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .mapper import CrawlerPageMapper
from .schemas import CrawledPage


class FileCrawlerClient:
    """Expose a local crawler export through the same operations as an API client."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        self._pages: list[CrawledPage] | None = None

    def _load_records(self) -> Iterable[dict[str, Any]]:
        suffix = self.path.suffix.lower()
        if suffix == ".csv":
            with self.path.open("r", encoding="utf-8-sig", newline="") as handle:
                yield from csv.DictReader(handle)
            return
        if suffix == ".json":
            with self.path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if isinstance(payload, list):
                yield from payload
            elif isinstance(payload, dict) and isinstance(payload.get("items"), list):
                yield from payload["items"]
            else:
                raise ValueError("JSON export must be an array or an object with an items array")
            return
        if suffix in {".parquet", ".pq"}:
            try:
                import pandas as pd
            except ImportError as exc:  # pragma: no cover - dependency is in requirements
                raise RuntimeError("Parquet support requires pandas and pyarrow") from exc
            dataframe = pd.read_parquet(self.path)
            yield from dataframe.to_dict(orient="records")
            return
        raise ValueError(f"Unsupported crawler export format: {self.path.suffix}")

    @property
    def pages(self) -> list[CrawledPage]:
        if self._pages is None:
            mapped: list[CrawledPage] = []
            for record in self._load_records():
                try:
                    mapped.append(CrawlerPageMapper.map_record(record))
                except ValueError:
                    # Preserve scanability: malformed rows are represented by a minimal page.
                    page_id = str(record.get("page_id") or record.get("id") or f"row-{len(mapped)}")
                    source_id = str(record.get("source_id") or record.get("source") or "unknown")
                    mapped.append(
                        CrawledPage(
                            page_id=page_id,
                            source_id=source_id,
                            url=str(record.get("url") or ""),
                            metadata={"_upstream_record": dict(record)},
                        )
                    )
            self._pages = mapped
        return self._pages

    def list_sources(self) -> list[dict[str, Any]]:
        grouped: OrderedDict[str, dict[str, Any]] = OrderedDict()
        for page in self.pages:
            source = grouped.setdefault(
                page.source_id,
                {"id": page.source_id, "name": page.metadata.get("source_name") or page.source_id, "page_count": 0},
            )
            source["page_count"] += 1
            if source["name"] == page.source_id:
                source["name"] = page.metadata.get("source_name") or page.source_id
        return sorted(grouped.values(), key=lambda item: str(item["id"]))

    def get_source(self, source_id: str) -> dict[str, Any]:
        for source in self.list_sources():
            if source["id"] == source_id:
                return source
        raise KeyError(source_id)

    def get_job(self, job_id: str) -> dict[str, Any]:
        """Derive a completed job summary when a local export has job IDs."""

        pages = self.list_pages(job_id=job_id)
        if not pages:
            raise KeyError(job_id)
        statuses = Counter(str(page.metadata.get("status") or "") for page in pages)
        skipped = sum(count for status, count in statuses.items() if status.startswith("SKIPPED"))
        failed = statuses.get("FAILED", 0)
        return {
            "id": job_id,
            "source_id": pages[0].source_id,
            "status": "COMPLETED",
            "crawl_config": {},
            "metadata": {
                "total_pages": len(pages),
                "in_queue_count": statuses.get("IN_QUEUE", 0),
                "success_count": len(pages) - failed - skipped - statuses.get("IN_QUEUE", 0),
                "unchanged_count": statuses.get("UNCHANGED", 0),
                "failed_count": failed,
                "skipped_count": skipped,
            },
        }

    def list_pages(
        self,
        source_id: str | None = None,
        limit: int | None = None,
        job_id: str | None = None,
    ) -> list[CrawledPage]:
        pages = [
            page
            for page in self.pages
            if (source_id is None or page.source_id == source_id)
            and (job_id is None or page.job_id == job_id)
        ]
        return pages[:limit] if limit is not None else pages

    def get_page(self, page_id: str) -> CrawledPage:
        for page in self.pages:
            if page.page_id == page_id:
                return page
        raise KeyError(page_id)
