# Crawler API observed schema

## Current workspace observation

The supplied local export is:

```text
data_test/parquet/crawl-pages.parquet
rows: 1062
```

Observed top-level columns:

| Upstream field | Type in export | Normalized field / note |
|---|---|---|
| `page_id` | string | `page_id` |
| `crawl_job_id` | string | `job_id` |
| `source_id` | string | `source_id` |
| `source_name` | string | source display name |
| `url` | string | `url` |
| `domain` | string | retained in `metadata` |
| `status` | string | crawler workflow status; not HTTP status |
| `kind` | string | retained in `metadata` |
| `source_hash` | string | retained in `metadata` |
| `content_type` | string/null | `content_type` |
| `metadata` | JSON string | nested HTTP/content metadata |
| `created_at` | ISO timestamp string | `crawled_at` |
| `updated_at` | ISO timestamp string | retained in `metadata` |
| `content` | string | `markdown` and fallback `extracted_text` |
| `depth` | int32 | retained in `metadata` |

Observed nested metadata keys include `error`, `links`, `title`, `warnings`, `final_url`, `pdf_scanned`, `skip_reason`, `status_code`, `content_route`, `links_truncated`, and `reused_from_source`.

## Remote API observed on `https://vin-auto-crawl.hotavn.com/`

The public Nuxt frontend config points at API version `v1.0`, and the public OpenAPI document is available at `/openapi.json`. The API is FastAPI-backed and uses `withCredentials` plus either a bearer token or `x-token` header. Anonymous probes on 2026-09-16 returned:

| Endpoint | Method | Anonymous result | Purpose |
|---|---|---:|---|
| `/api-non/v1.0/users/setup-status` | GET | 200 | Setup/registration flags. |
| `/api-non/v1.0/users/login` | POST | not submitted | Login body is `{"email": string, "password": string}`; response contains `data.user_id`, `token`, `refresh_token`, expiry fields. |
| `/api-non/v1.0/users/refresh-token` | POST | not submitted | Body `{"refresh_token": string}`. |
| `/api/v1.0/crawl/sources` | GET | 401 | Sources list; query `page`, `page_size`, `enabled`, `domain`. |
| `/api/v1.0/crawl/sources/{source_id}` | GET | 401 | Source detail. |
| `/api/v1.0/crawl/jobs` | GET | 401 | Jobs list; query `page`, `page_size`, `source_id`, `status`, `domain`. |
| `/api/v1.0/crawl/jobs/{job_id}` | GET | 401 | Job detail. |
| `/api/v1.0/crawl/pages` | GET | 401 | Page list; query `page`, `page_size`, `job_id`, `status[]`, `kind[]`, `domain`. |
| `/api/v1.0/crawl/pages/{page_id}` | GET | 401 | Page metadata/detail. |
| `/api/v1.0/crawl/pages/{page_id}/view` | GET | 401 | Rendered page view; returns `markdown` and/or signed `download_url`. |
| `/api/v1.0/crawl/pages/{page_id}/download` | GET | 401 | Raw or processed page download; query `raw`, `expires_seconds`. |
| `/api/v1.0/crawl/pages/{page_id}/clean-preview` | GET | 401 | Clean preview; query required `clean_mode`, optional `scope`. |
| `/api/v1.0/crawl/exports` | GET/POST | 401 | Export jobs; list query `page`, `page_size`. |
| `/api/v1.0/crawl/exports/{export_id}` | GET | 401 | Export status. |
| `/api/v1.0/crawl/exports/{export_id}/download` | GET | 401 | Signed export download. |

The source, job, and page list responses are paginated envelopes with `items`, `total`, `page`, and `page_size`. The OpenAPI schema for page records is `CrawlPageResponse` and has `id`, `crawl_job_id`, `url`, `domain`, `source_hash`, `content_type`, `s3_key`, `raw_s3_key`, `links_s3_key`, `retry_count`, `depth`, `kind`, `status`, `ref_crawl_page_id`, `proxy_id`, `metadata`, `failure`, `created_at`, `updated_at`, and `degraded`. `metadata` includes `links`, `links_truncated`, `title`, `status_code`, `final_url`, `warnings`, `content_route`, `pdf_scanned`, `skip_reason`, `reused_from_source`, and `error`. Page content is exposed separately by the `/view` response (`crawl_page_id`, `url`, `content_type`, `markdown`, `download_url`, `assets`, `truncated`).

The source schema is `SourceResponse`: `id`, `url`, `display_name`, `domain`, `enabled`, `crawl_config`, `rules`, `next_run_at`, `created_at`, `updated_at`, and `degraded`. The job schema is `JobResponse`: `id`, `source_id`, `domain`, `status`, `started_at`, `finished_at`, `crawl_config`, `metadata`, `created_at`, `updated_at`, and `degraded`.

## Remote discovery contract

Set `CRAWLER_BASE_URL` and credentials in a local `.env`. The CLI adapter is planned; the current discovery implementation is available as `CrawlerDiscovery.probe()` and is covered by unit tests. Future CLI/API adapters must call this same read-only implementation rather than duplicate discovery logic.

The client probes `CRAWLER_SOURCES_PATH`, `CRAWLER_PAGES_PATH`, and `CRAWLER_PAGE_DETAIL_PATH` first when configured, followed by conservative candidates such as `/api/sources`, `/sources`, `/api/pages`, and `/pages`. The discovery report records method, path, status, pagination shape, and JSON keys. It redacts authorization, cookies, and credential values.

After discovery, set explicit endpoint paths in `.env` and update this file with the observed method, query parameters, pagination field, auth mechanism, and a sanitized sample response. The client does not silently invent an upstream mapping when the response is not JSON or required identifiers are missing; it raises `UPSTREAM_SCHEMA_CHANGED`.

## Authenticated live observations

On 2026-09-16, a read-only authenticated probe succeeded using credentials supplied through the local environment. Secrets and tokens were not recorded. The probe observed:

- 23 sources visible to the authenticated user.
- Source, job, page, page view, clean mode, clean preview, and export list GET operations.
- Clean modes `RAW`, `LIGHT`, `HEAVY`, and `SAFE`; HEAVY can return a degraded fallback to LIGHT.
- Page `kind` is independent from response `content_type`; a `RESOURCE` URL ending in `.png`/`.svg` can return `text/html` after redirect.
- A Foody job with runtime `max_pages=1200` and `max_resources=20000` reported an effective record budget of 21200. The source budget was edited after the job started, so this is not evidence that the crawler changed runtime configuration unexpectedly. It is evidence that Page budget/Resource budget semantics, defaults, and the visibility of runtime overrides need clearer UX and diagnostics.
- Sampled Foody resource URLs included repeated path segments and redirects to external HTML hosts; this motivated `diagnose_crawl_stall`, `analyze_resource_mix`, and `explain_page_classification`.

These observations are evidence for tool behavior and regression tests, not a guarantee that future jobs have the same values.

## PyTorch failure observation

The source `Pytorch` (`pytorch.org`) had two consecutive completed jobs with the same systemic pattern:

- 108 page records observed per job;
- 80 `FAILED`, mostly `NAVIGATION` records;
- all 80 failures had `CRW_PERMANENT`;
- all 80 contained `js_escalation_failed` with either `CDP discovery failed: error sending request` or `CDP Target.createTarget: WS closed`;
- all 80 had no HTTP status and were marked non-retryable;
- the source/runtime config had `render_js: null`, so the renderer escalation path was selected by the crawler.

This evidence indicates a crawler browser/renderer/CDP failure before the HTTP response was recorded, not 80 target-site HTTP errors. It motivated the `diagnose_failed_pages` tool. No retry, cancel, or configuration mutation was performed.
