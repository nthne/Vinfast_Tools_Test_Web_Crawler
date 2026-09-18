# Agent Tool-First Web Crawl QA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Web Crawl QA project into a read-only agent-toolkit that answers recurring crawler inspection questions with structured evidence and records new reusable tools as they are discovered.

**Architecture:** `agent_tools` provides a stable `ToolResult`, a registry, a small question-to-tool router, and read-only inspection tools built on the existing crawler clients. Tool logic returns observed metrics, hypotheses, confidence, recommended actions, and optional new-tool proposals; it never mutates crawler state. The README and tool catalog are updated to describe this as a crawler-testing toolkit, not as a crawler web application.

**Tech Stack:** Python 3.11+, dataclasses, existing `HttpCrawlerClient`/`FileCrawlerClient`, pytest, JSON-safe result dictionaries.

**Spec:** `docs/agent_tools.md` and `docs/superpowers/specs/2026-09-16-web-crawl-qa-tool-design.md`

## Global Constraints

- Credentials remain environment-only and must never appear in tool inputs, results, logs, or docs.
- Tools are read-only against the upstream crawler except for the login POST required by the auth provider.
- A tool must distinguish observed evidence from inferred hypotheses.
- If a question has no suitable registered tool, the router returns a proposal instead of silently inventing a mutation.
- Existing crawler client normalization remains the boundary; tools must not depend on raw upstream field names unnecessarily.
- Every new production function gets a failing test before implementation.

---

### Task 1: Tool result contract and registry

**Files:**
- Create: `agent_tools/__init__.py`
- Create: `agent_tools/models.py`
- Create: `agent_tools/registry.py`
- Test: `tests/unit/test_agent_tools_registry.py`

**Interfaces:**
- `ToolResult.to_dict() -> dict[str, Any]`
- `ToolRegistry.register(name, description, handler) -> None`
- `ToolRegistry.list_tools() -> list[dict[str, str]]`
- `ToolRegistry.run(name, **kwargs) -> ToolResult`
- `ToolRegistry.propose(question, reason) -> ToolResult`

- [ ] Write tests for JSON-safe results, read-only default, registered tool execution, unknown tool proposals, and secret redaction from result values.
- [ ] Run `python -m pytest tests/unit/test_agent_tools_registry.py -q` and verify the missing-module failure.
- [ ] Implement the smallest dataclass contract and registry.
- [ ] Run the focused test and then the existing suite.

### Task 2: Public read-only client methods needed by tools

**Files:**
- Modify: `crawler_client/http_client.py`
- Modify: `crawler_client/file_client.py`
- Test: `tests/unit/test_http_client.py`, `tests/unit/test_file_client.py`

**Interfaces:**
- `HttpCrawlerClient.get_job(job_id) -> dict[str, Any]`
- `HttpCrawlerClient.get_page_view(page_id) -> dict[str, Any]`
- `HttpCrawlerClient.list_clean_modes() -> dict[str, Any]`
- `HttpCrawlerClient.preview_clean(page_id, clean_mode, scope="PAGE") -> dict[str, Any]`
- `HttpCrawlerClient.list_exports(limit=None) -> list[dict[str, Any]]`
- `FileCrawlerClient.get_job(job_id) -> dict[str, Any]` returns a clear unsupported/read-only-local result or raises a documented `CrawlerAPIError`-compatible exception.

- [ ] Write tests for actual observed endpoint paths, clean-preview params, export pagination and response unwrapping.
- [ ] Run focused client tests and verify failures before implementation.
- [ ] Add public wrappers over the existing safe GET path; do not expose private request calls to tools.
- [ ] Run focused client tests and the full suite.

### Task 3: Inspection tools for source/job/page/resource classification

**Files:**
- Create: `agent_tools/<tool_name>/tool.py` and `README.md`
- Modify: `agent_tools/__init__.py`
- Test: `tests/unit/test_agent_tool_inspection.py`

**Interfaces:**
- `inspect_source(client, source_id) -> ToolResult`
- `inspect_job(client, job_id, sample_pages=0) -> ToolResult`
- `inspect_page(client, page_id) -> ToolResult`
- `analyze_resource_mix(client, job_id, sample_pages=8, page_size=100) -> ToolResult`
- `explain_page_classification(client, page_id) -> ToolResult`

- [ ] Write tests using a fake read-only client for source config, job counters, page metadata, resource MIME distribution, and `RESOURCE` plus `text/html` classification.
- [ ] Run the focused tests and verify the expected missing-module failures.
- [ ] Implement structured metrics without returning full page content or secrets.
- [ ] Add evidence for `kind`, `content_type`, `content_route`, redirect warnings, host, depth and URL-shape anomalies.
- [ ] Run focused tests and all existing tests.

### Task 4: Clean and provenance tools

**Files:**
- Create: `agent_tools/<tool_name>/tool.py` and `README.md`
- Modify: `agent_tools/__init__.py`
- Test: `tests/unit/test_agent_tool_cleaning.py`

**Interfaces:**
- `compare_clean_modes(client, page_id, modes=None) -> ToolResult`
- `explain_clean_output_length(client, page_id, mode="SAFE") -> ToolResult`
- `check_raw_provenance(client, page_id) -> ToolResult`
- `inspect_export_cleaning(client, limit=None) -> ToolResult`

- [ ] Write tests for RAW/LIGHT/HEAVY/SAFE retention, HEAVY degraded fallback, output expansion, `matches_export`, and export cleaning reports.
- [ ] Run the focused tests and verify failures.
- [ ] Implement numeric comparisons with explicit `observed` versus `inferred` evidence and no semantic-content claim when only lengths are available.
- [ ] Run focused cleaning tests and all tests.

### Task 5: Crawl-stall and budget diagnostic

**Files:**
- Create: `agent_tools/diagnose_crawl_stall/tool.py` and `README.md`
- Modify: `agent_tools/__init__.py`, `docs/agent_tools.md`
- Test: `tests/unit/test_agent_tool_job_diagnostics.py`

**Interfaces:**
- `diagnose_crawl_stall(client, job_id, poll_seconds=0, sample_pages=(1, 2, 10)) -> ToolResult`

- [ ] Write tests for combined navigation/resource budget, explicit source/runtime overrides, unchanged queue polling, repeated path segments, and the distinction between exact duplicates and URL expansion.
- [ ] Run the focused tests and verify failures.
- [ ] Implement bounded polling, URL-shape sampling and classifications `PROGRESSING`, `BUDGET_EXHAUSTED`, `URL_EXPANSION_SUSPECTED`, `STALLED`, and `UNKNOWN`.
- [ ] Ensure the tool never calls run/cancel/delete/create-export endpoints.
- [ ] Run focused diagnostics tests and the full suite.

### Task 6: Router, README direction and tool catalog synchronization

**Files:**
- Create: `agent_tools/router.py`
- Modify: `agent_tools/__init__.py`
- Modify: `README.md`
- Modify: `docs/agent_tools.md`
- Modify: `docs/crawler_api_observed.md`
- Test: `tests/unit/test_agent_tool_router.py`

**Interfaces:**
- `route_question(question: str) -> dict[str, Any]`
- `default_registry(client) -> ToolRegistry`

- [ ] Write tests mapping the real questions to `diagnose_crawl_stall`, `analyze_resource_mix`, `explain_page_classification`, `explain_clean_output_length`, and `check_raw_provenance`.
- [ ] Run the focused tests and verify failures.
- [ ] Implement deterministic keyword routing for known capabilities and a structured `new_tool_proposal` for unknown questions.
- [ ] Rewrite README around the agent-toolkit workflow, local/live read-only usage, tool catalog, and future adapters; remove claims that CLI/FastAPI/dashboard already exist.
- [ ] Update observed API docs to distinguish anonymous discovery from authenticated live observations.
- [ ] Run all tests, compileall, and local tool smoke checks.
