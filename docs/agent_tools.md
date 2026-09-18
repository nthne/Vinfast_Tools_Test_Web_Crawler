# Agent tools

The agent uses a small set of read-only, evidence-first tools for questions about the crawler platform. Tools are selected by intent rather than by matching a question string exactly.

## Tool selection policy

1. Match the request to an existing tool by its capability and required evidence.
2. If no tool is sufficient, use the narrowest read-only API calls available to investigate the request.
3. Return observed evidence, inferred hypotheses, confidence, and recommended next checks.
4. Propose a new tool when the investigation is reusable; do not silently create a mutating tool.
5. Record the proposed tool in this document; after user approval, add production behavior through a failing test and a read-only implementation.

All crawler tools must:

- read credentials only from environment/secret storage;
- avoid returning credentials, tokens, cookies, signed URLs, or full page content by default;
- use the HTTP client's safe GET allowlist;
- return structured evidence instead of an unexplained score;
- continue per page/item when one upstream record is malformed.

## Package convention

Mỗi tool implementation nằm trong package riêng:

```text
agent_tools/<tool_name>/
  tool.py
  README.md
```

`models.py`, `registry.py` và `router.py` là hạ tầng dùng chung. Mỗi tool package chỉ giữ implementation của chính tool đó.

## Tool catalog

The registry currently implements `inspect_source`, `inspect_job`, `inspect_page`, `explain_page_classification`, `analyze_resource_mix`, `compare_clean_modes`, `explain_clean_output_length`, `check_raw_provenance`, `inspect_export_cleaning`, `diagnose_crawl_stall`, `diagnose_failed_pages`, `diagnose_out_of_scope_urls`, `diagnose_url_404_mismatch`, `audit_crawl_history`, `export_crawler_error_report`, and `route_question`. The page/source QA runners remain planned contracts, not yet registered tools.

## Tool: `export_crawler_error_report`

Writes one detailed Markdown artifact per error signature and updates one cumulative Markdown summary for crawler developers. It also accepts supplemental diagnostic findings, such as `SOURCE_URL_MISSING_TRAILING_SLASH`, under a separate `Additional QA findings` section so they do not inflate page-failure counts. Detail reports contain job summary, failure rate, status/kind distribution, affected page rows, runtime config, evidence, and recommended actions. URLs omit query strings/fragments and the tool never mutates the crawler platform.

Default output:

```text
artifacts/crawler_error_reports/errors/<error_code>_<signature>.md
artifacts/crawler_error_reports/crawler_error_summary.md
```

The detail files are organized by distinct error signature (`error_code` +
message). The summary aggregates observations across all job IDs reported
through this tool and replaces an existing run entry when the same job is
reported again.

## Tool: `diagnose_url_404_mismatch`

Compares a current upstream document URL with matching crawler candidates. It
probes both sides read-only and distinguishes a stale/versioned crawler path
from a genuine upstream 404. It is useful when a document moved from an
unversioned path such as `/docs/utils.html` to a versioned path such as
`/docs/2.14/utils.html`.

## Tool: `diagnose_out_of_scope_urls`

Explains why a source such as Foody produces Microsoft, X/Twitter or other
unrelated URLs. It checks both persisted page rows and the `metadata.links`
of each sampled page, then separates:

- external `NAVIGATION` pages from legitimate external assets;
- `RESOURCE` URLs that return `text/html` and still contain links;
- asset-extension URLs returning HTML after a redirect;
- binary/image MIME attached to a `NAVIGATION` record;
- repeated path segments that can amplify URL expansion.

Evidence observed in the Foody jobs includes `x.com/apple-touch-icon.png`
stored as `RESOURCE` with `text/html`, Microsoft resource URLs with deeply
repeated `/media/...` paths and redirect warnings, and
`abs.twimg.com/favicons/twitter.3.ico` stored as `NAVIGATION` while its MIME
is `image/vnd.microsoft.icon`. This confirms that `kind` is based on
discovery context rather than MIME alone.

The most likely crawler defect is that the resource fetch path parses and
expands links from HTML returned for an asset URL, while the navigation
allowlist does not reject the resulting external hosts. The tool reports
evidence without modifying crawler policy or job data.

## Tool: `audit_crawl_history`

Audits historical jobs for selected sources/date ranges and writes a natural-language Markdown report. It groups failure causes into renderer/CDP, retry exhaustion, proxy/403, anti-bot, SSRF/DNS security, download HTTP status, extraction structure, and URL expansion. It also records metadata/page-endpoint count mismatches and resource MIME mix.

| Tool | Purpose | Typical questions |
|---|---|---|
| `discover_crawler_capabilities` | Observe safe endpoints and response schemas | “Crawler có những function nào?” |
| `inspect_source` | Read source URL, domain, enabled state, crawl config, rules | “Source này cấu hình thế nào?” |
| `inspect_job` | Read job status, counters, timestamps, failures, runtime config | “Job này lỗi gì?” |
| `inspect_page` | Read page metadata, view metadata, content lengths and page errors | “Page này có vấn đề gì?” |
| `explain_page_classification` | Explain `NAVIGATION` versus `RESOURCE` using discovery context and response metadata | “Vì sao text/html lại là resource?” |
| `analyze_resource_mix` | Break down resources by kind, content type, host, route and budget usage | “Vì sao resource hầu hết là ảnh?” |
| `compare_clean_modes` | Compare RAW/LIGHT/HEAVY/SAFE output metrics | “Clean nhẹ và sâu khác nhau thế nào?” |
| `explain_clean_output_length` | Explain output/input length changes with measurements | “Tại sao SAFE dài hơn input?” |
| `check_raw_provenance` | Compare page view, clean preview and export artifact provenance | “RAW preview có giống raw không?” |
| `inspect_export_cleaning` | Inspect export status and cleaning report | “Export HEAVY có thực sự dùng LLM không?” |
| `route_question` | Map a recurring question to a capability or return a new-tool proposal | “Agent nên gọi tool nào?” |
| `run_page_qa` | Run modular page-level QA rules | “Page này có lỗi extraction không?” |
| `run_source_qa` | Run source-level QA with profile and duplicate context | “Toàn source có bao nhiêu lỗi?” |
| `export_qa_report` | Export QA findings to CSV/JSON/Parquet | “Xuất báo cáo QA” |

## Tool: `diagnose_crawl_stall`

This tool was identified while investigating Foody job `49ddbae0-3320-4d15-9ffa-eeaf69099d68`. Basic `inspect_job` can show that a job is running, but it cannot distinguish a legitimate resource budget from a URL expansion trap or a stalled worker.

### Input

```json
{
  "job_id": "string",
  "poll_seconds": 10,
  "url_sample_pages": [1, 2, 10, 50, 100, 150, 200]
}
```

### Read-only checks

- job status, timestamps and runtime `crawl_config`;
- current source configuration for comparison;
- page envelope total and status/kind/depth samples;
- exact duplicate URLs and normalized route variants;
- repeated path segments, URL length and query-parameter explosion;
- resource versus navigation budget;
- queue progress and `updated_at` across a bounded poll;
- failure, skip, redirect and warning signals.

### Output contract

```json
{
  "answer": "...",
  "classification": "RUNNING|PROGRESSING|BUDGET_EXHAUSTED|URL_EXPANSION_SUSPECTED|STALLED|UNKNOWN",
  "evidence": [],
  "metrics": {},
  "hypotheses": [],
  "recommended_actions": [],
  "new_tool_proposal": null,
  "read_only": true
}
```

The tool must not call run, cancel, delete, create export, upload, import, proxy mutation, policy mutation, or system-value mutation endpoints.

### Related error codes

```text
JOB_STALLED
JOB_BUDGET_EXHAUSTED_NOT_TERMINATED
JOB_RUNTIME_CONFIG_DIFFERS_FROM_SOURCE
URL_PATH_EXPANSION
URL_RESOURCE_TRAP
URL_CANONICALIZATION_INEFFECTIVE
RESOURCE_BUDGET_OVERRIDDEN
```

## Tool: `analyze_resource_mix`

This tool explains why a crawl spends its resource budget on images or other assets instead of navigation content.

### Read-only checks

- resource versus navigation counts;
- `content_type` distribution such as image, CSS, JavaScript, PDF and HTML;
- source host versus external host distribution;
- asset URL patterns such as favicon, tracking pixel, `srcset` and repeated path segments;
- resource counts by depth and page budget usage;
- whether `only_main_content` and URL rules allow broad asset collection.

### Related error codes

```text
RESOURCE_MIX_IMAGE_HEAVY
RESOURCE_BUDGET_DOMINATED
EXTERNAL_RESOURCE_OVER_COLLECTION
RESOURCE_CONTENT_TYPE_MISMATCH
RESOURCE_RULE_NOT_RESTRICTIVE
```

## Tool: `explain_page_classification`

`kind` is assigned from how the crawler discovered a URL, while `content_type` is observed after the HTTP response. These are independent dimensions and must not be inferred from the file extension alone.

The tool should inspect `kind`, requested URL, final URL, content type, content route, redirect warnings, referrer page and discovery context such as HTML tag/attribute when the upstream API exposes them. If discovery context is unavailable, it must return an explicit `UNKNOWN_CONTEXT` result instead of guessing.

### Related error codes

```text
RESOURCE_URL_RETURNS_HTML
NAVIGATION_URL_RETURNS_BINARY
REDIRECT_RESOURCE_TO_HTML
DISCOVERY_CONTEXT_UNAVAILABLE
```

## Proposed tool: `diagnose_job_failure_root_cause`

Status: proposed from the PyTorch investigation; awaiting approval before implementation.

This tool is needed when a user asks why many or all pages in a job show a generic failure such as `The system gave up`. It must separate crawler-pipeline failures from upstream HTTP/content failures instead of reporting only the UI message.

### Input

```json
{
  "job_id": "string",
  "sample_failed_pages": 10,
  "probe_upstream_http": true
}
```

### Read-only checks

- job status, counts, runtime configuration and error summary;
- page status/kind/content type/error grouped by host and failure code;
- representative failed page metadata and retryability;
- bounded upstream GET probes for representative URLs, recording status, final URL, MIME and response size only;
- comparison with skipped/successful pages from the same job;
- repeated-failure detection across previous jobs for the same source.

### Output contract

```json
{
  "classification": "CRAWLER_RENDERER_FAILURE|UPSTREAM_HTTP_FAILURE|MIXED_FAILURE|UNKNOWN",
  "evidence": [],
  "metrics": {},
  "hypotheses": [],
  "recommended_actions": [],
  "read_only": true
}
```

### PyTorch evidence that motivated this tool

- Both recent Pytorch jobs had 108 records and 80 failed pages.
- All 80 failed records were under `docs.pytorch.org` and reported `js_escalation_failed` with CDP discovery/target WebSocket errors.
- A representative failed URL returned HTTP 404 directly, while representative skipped documentation URLs returned HTTP 200.
- The source and runtime `render_js` setting was unset, so the tool must expose when an automatic JS escalation path is invoked despite no explicit render setting.
