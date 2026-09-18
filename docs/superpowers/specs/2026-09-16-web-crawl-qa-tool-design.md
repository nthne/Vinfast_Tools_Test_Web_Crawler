# Web Crawl QA Tool Design

## Goal

Build a read-only, explainable QA tool for authenticated crawler data that can inspect the supplied crawl export immediately and later connect to the real crawler platform through environment-configured HTTP authentication.

## Scope and assumptions

- The workspace currently contains a 1,062-row Parquet export and no crawler base URL or credentials.
- The first usable path is local Parquet/CSV/JSON ingestion; network discovery is implemented as a generic, configurable adapter and is not allowed to guess production schema silently.
- The MVP runs on Python 3.11+ and uses FastAPI, httpx, SQLite, pandas/pyarrow, and pytest.
- All crawler access is read-only. No delete, update, recrawl, CAPTCHA bypass, proxy rotation, or LLM-wide scan is included.

## Architecture

`CrawlerClient` exposes sources, pages, and page details independently of the upstream schema. `FileCrawlerClient` handles the supplied export and `HttpCrawlerClient` handles authenticated JSON endpoints. `CrawlerPageMapper` converts upstream records into `CrawledPage`, so QA rules never depend on crawler-specific field names.

`QAEngine` runs registered stateless rules against a page plus a prebuilt `QAContext`. The context contains an exact-content duplicate index and optional source profile. Every finding is a structured `QAError` with evidence and recommended action. A scan service persists scan metadata, page snapshots, and error rows to SQLite; the export service emits flat error rows as CSV/JSON/Parquet plus a source summary.

FastAPI exposes health, sources, pages, scan, error, diff, export, and discovery endpoints. A small server-rendered dashboard consumes those endpoints and supports source selection, scan mode, error/severity filters, and page detail content tabs.

## Data flow

1. Load credentials/config from environment (never source code).
2. Select local file client when `CRAWLER_DATA_PATH` is set; otherwise construct HTTP client from `CRAWLER_BASE_URL`.
3. Discover or configure upstream endpoints and record observed endpoint metadata without secrets.
4. Fetch pages with pagination, normalize each record, and isolate per-page errors.
5. Build exact duplicate index and run the 15 MVP rules.
6. Persist scan and findings, calculate overview statistics, and export a flattened report.

## MVP rules

The registry contains: `HTTP_404`, `HTTP_429`, `HTTP_5XX`, `AUTH_REDIRECT_TO_LOGIN`, `AUTH_LOGIN_PAGE_RETURNED`, `EMPTY_PAGE`, `VERY_LOW_CONTENT`, `SOFT_404`, `CAPTCHA_PAGE`, `ANTI_BOT_PAGE`, `ENCODING_MOJIBAKE`, `UNICODE_REPLACEMENT_CHAR`, `CLEAN_RESULT_EMPTY`, `CLEANING_OVER_AGGRESSIVE`, and `EXACT_DUPLICATE_CONTENT`.

Each rule is independently testable and returns zero or more findings. Rule failures do not abort the page or scan. Missing upstream fields remain `None`; rules only evaluate when their evidence is available.

## Authentication and discovery

- `ApiKeyAuth` injects `Authorization: Bearer …` when `CRAWLER_API_KEY` exists.
- `SessionAuth` tries configured `CRAWLER_LOGIN_PATH` first, then common login paths, and retains cookies in an `httpx.Client`.
- `AuthMode=auto` chooses API key first, then session login, and reports `AUTH_FAILED` with a safe reason when no usable mode is configured.
- `PlaywrightAuth` is an optional adapter boundary documented for JS/SSO flows; the MVP does not automate CAPTCHA or infer credentials.
- `CrawlerDiscovery` probes configured/common read endpoints and records method, path, status, pagination hints, and redacted JSON keys in `docs/crawler_api_observed.md` or a user-selected output.

## Persistence and export

SQLite tables store `scans`, `page_results`, and `qa_errors`. Page snapshots are JSON so raw/extracted/cleaned content remains available for evidence and diff view. Export rows include source/page/url/status/severity/code/category/message/metric/observed/threshold/action; summary includes page and error rates.

## Security

`.env` and auth artifacts are ignored. Logs and discovery output never include passwords, bearer tokens, or cookies. The HTTP client only implements GET plus the login POST required for authentication. The dashboard has no mutation controls for crawler data.

## Testing strategy

- Unit tests use small in-memory `CrawledPage` objects and fixture HTML/text, covering every required rule, mapper, URL/data loading, exports, and persistence.
- Integration tests use an in-process fake HTTP transport or local file fixture and never require real credentials.
- Live integration is opt-in through `CRAWLER_BASE_URL` and credentials, with a sample-first workflow documented in the README.
