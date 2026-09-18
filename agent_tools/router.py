"""Compatibility router and default registry for crawler agent tools."""

from __future__ import annotations

from typing import Any

from .analyze_resource_mix import analyze_resource_mix
from .audit_crawl_history import audit_crawl_history
from .check_raw_provenance import check_raw_provenance
from .compare_clean_modes import compare_clean_modes
from .diagnose_crawl_stall import diagnose_crawl_stall
from .diagnose_failed_pages import diagnose_failed_pages
from .diagnose_out_of_scope_urls import diagnose_out_of_scope_urls
from .diagnose_url_404_mismatch import diagnose_url_404_mismatch
from .explain_clean_output_length import explain_clean_output_length
from .explain_page_classification import explain_page_classification
from .export_crawler_error_report import export_crawler_error_report
from .inspect_export_cleaning import inspect_export_cleaning
from .inspect_job import inspect_job
from .inspect_page import inspect_page
from .inspect_source import inspect_source
from .models import ToolResult
from .registry import ToolRegistry
from .route_question import route_question


def default_registry(client: Any) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("inspect_source", "Inspect source configuration", lambda source_id: inspect_source(client, source_id))
    registry.register("inspect_job", "Inspect job status and counters", lambda job_id, sample_pages=0: inspect_job(client, job_id, sample_pages))
    registry.register("inspect_page", "Inspect page metadata and content lengths", lambda page_id: inspect_page(client, page_id))
    registry.register(
        "analyze_resource_mix",
        "Analyze resource kinds and MIME mix",
        lambda job_id, sample_pages=8, page_size=100: analyze_resource_mix(client, job_id, sample_pages, page_size),
    )
    registry.register("explain_page_classification", "Explain navigation/resource classification", lambda page_id: explain_page_classification(client, page_id))
    registry.register("compare_clean_modes", "Compare clean modes", lambda page_id, modes=None: compare_clean_modes(client, page_id, modes))
    registry.register("explain_clean_output_length", "Explain clean output length", lambda page_id, mode="SAFE": explain_clean_output_length(client, page_id, mode))
    registry.register("check_raw_provenance", "Compare page view and RAW preview provenance", lambda page_id: check_raw_provenance(client, page_id))
    registry.register("inspect_export_cleaning", "Inspect export cleaning reports", lambda limit=None: inspect_export_cleaning(client, limit))
    registry.register(
        "export_crawler_error_report",
        "Write per-error detail reports and update a cumulative Markdown summary",
        lambda job_id, output_path=None, sample_pages=None, max_page_rows=200, output_dir=None, summary_path=None, diagnostic_findings=None: export_crawler_error_report(
            client, job_id, output_path, sample_pages, max_page_rows, output_dir, summary_path, diagnostic_findings
        ),
    )
    registry.register("diagnose_failed_pages", "Diagnose systematic page failures", lambda job_id, sample_pages=None: diagnose_failed_pages(client, job_id, sample_pages))
    registry.register(
        "diagnose_out_of_scope_urls",
        "Explain external URLs and page/resource scope leakage",
        lambda job_id, sample_pages=None: diagnose_out_of_scope_urls(client, job_id, sample_pages),
    )
    registry.register(
        "diagnose_url_404_mismatch",
        "Compare crawler 404 URLs with the current upstream document URL",
        lambda job_id, expected_url, sample_pages=None, max_probes=20, request_timeout=15.0: diagnose_url_404_mismatch(
            client, job_id, expected_url, sample_pages, max_probes, request_timeout
        ),
    )
    registry.register("diagnose_crawl_stall", "Diagnose queue, budget and URL expansion", lambda job_id, poll_seconds=0, sample_pages=(1, 2, 10): diagnose_crawl_stall(client, job_id, poll_seconds, sample_pages))
    registry.register(
        "audit_crawl_history",
        "Audit historical jobs and explain failure causes",
        lambda source_keywords=None, start_date=None, end_date=None, output_path=None, include_cancelled=True: audit_crawl_history(
            client, source_keywords, start_date, end_date, output_path, include_cancelled
        ),
    )
    return registry


__all__ = ["ToolResult", "ToolRegistry", "default_registry", "route_question"]
