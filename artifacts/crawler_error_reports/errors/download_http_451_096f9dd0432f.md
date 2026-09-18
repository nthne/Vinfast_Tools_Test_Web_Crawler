# Detailed Crawler Error Report

## Error signature: `DOWNLOAD_HTTP_451`

**Message:** Download failed with HTTP 451

## Impact

| Metric | Value |
|---|---:|
| Job ID | `49ddbae0-3320-4d15-9ffa-eeaf69099d68` |
| Source ID | `c306f333-5aaa-4325-abea-9ab2c276bdec` |
| Pages with this error in this job | 1 |
| All failed pages in this job | 592 |
| Share of failed pages | 0.2% |
| Generated at (UTC) | `2026-09-18T05:01:40.972729+00:00` |

## Evidence

- Status/kind distribution: `{'RESOURCE': 1}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 1}`
- Retryable distribution: `{'False': 1}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 1200, 'max_resources': 20000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `cfe4ed6e-06b7-4bc6-b7de-170998aa979c` | `RESOURCE` | - | False | `https://avatars.discourse-cdn.com/v4/letter/s/d26b3c/25.png` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
