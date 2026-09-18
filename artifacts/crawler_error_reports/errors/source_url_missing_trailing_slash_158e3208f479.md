# Detailed Crawler Diagnostic Report

## Finding: `SOURCE_URL_MISSING_TRAILING_SLASH`

**Message:** Relative links resolve against a source URL without a trailing slash

## Impact

This is a crawler QA diagnostic finding. It is reported separately from page-failure counts.

| Metric | Value |
|---|---|
| `job_id` | `c5a658df-6d8d-45ef-bfc8-3ccb9e8b1773` |
| `expected_url` | `https://docs.pytorch.org/docs/2.14/utils.html` |
| `expected_status_code` | `200` |
| `crawler_page_count` | `108` |
| `candidate_count` | `1` |
| `probed_candidate_count` | `1` |
| `crawler_404_count` | `0` |
| `upstream_404_count` | `1` |
| `mismatch_count` | `1` |
| `expected_final_url` | `https://docs.pytorch.org/docs/2.14/utils.html` |
| `expected_content_type` | `text/html; charset=utf-8` |
| `source_url` | `https://docs.pytorch.org/docs/main` |
| `source_url_has_trailing_slash` | `False` |
| `relative_resolution_without_slash` | `https://docs.pytorch.org/docs/utils.html` |
| `relative_resolution_with_slash` | `https://docs.pytorch.org/docs/main/utils.html` |
| `relative_link_root_cause` | `SOURCE_URL_MISSING_TRAILING_SLASH` |

## Observed evidence

### Observation 1

- `page_id`: `a9e7dd36-5934-42d7-be13-ff0db2cd2abc`
- `crawler_url`: `https://docs.pytorch.org/docs/utils.html`
- `crawler_status_code`: `-`
- `upstream_status_code`: `404`
- `upstream_final_url`: `https://docs.pytorch.org/docs/utils.html`
- `upstream_content_type`: `text/html; charset=utf-8`
- `probe_error`: `-`

## Recommended actions

1. Verify the source seed URL and link extraction rule that produced the crawler path.
2. Check whether the crawler follows the current versioned documentation links.
3. Re-run one page after correcting the seed/path rule before starting a full crawl.

## Safety

- This finding was recorded from read-only crawler/API and upstream probes.
- Query strings and fragments are omitted from URL evidence.
- No retry, cancel, delete, or crawler configuration mutation was performed.
- Generated at (UTC): `2026-09-18T04:01:57.026920+00:00`
