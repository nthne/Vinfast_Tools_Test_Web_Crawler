# Detailed Crawler Error Report

## Error signature: `CRW_PERMANENT`

**Message:** No usable content could be extracted (Structural: no <body> tag (1369 bytes))

## Impact

| Metric | Value |
|---|---:|
| Job ID | `d61f29db-0079-46dd-82c5-23a159f8ea17` |
| Source ID | `c306f333-5aaa-4325-abea-9ab2c276bdec` |
| Pages with this error in this job | 3 |
| All failed pages in this job | 87 |
| Share of failed pages | 3.4% |
| Generated at (UTC) | `2026-09-18T04:01:00.995416+00:00` |

## Evidence

- Status/kind distribution: `{'NAVIGATION': 3}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 3}`
- Retryable distribution: `{'False': 3}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 10000, 'max_resources': 20000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `17735055-e799-4a76-9554-46e1d12b62f2` | `NAVIGATION` | - | False | `https://www.google.com/intl/en/policies/terms` |
| 2 | `17735055-e799-4a76-9554-46e1d12b62f2` | `NAVIGATION` | - | False | `https://www.google.com/intl/en/policies/terms` |
| 3 | `17735055-e799-4a76-9554-46e1d12b62f2` | `NAVIGATION` | - | False | `https://www.google.com/intl/en/policies/terms` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
