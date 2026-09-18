# Detailed Crawler Error Report

## Error signature: `CRW_PERMANENT`

**Message:** Target returned 400 Bad Request

## Impact

| Metric | Value |
|---|---:|
| Job ID | `d61f29db-0079-46dd-82c5-23a159f8ea17` |
| Source ID | `c306f333-5aaa-4325-abea-9ab2c276bdec` |
| Pages with this error in this job | 6 |
| All failed pages in this job | 87 |
| Share of failed pages | 6.9% |
| Generated at (UTC) | `2026-09-18T04:01:00.995416+00:00` |

## Evidence

- Status/kind distribution: `{'NAVIGATION': 6}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 6}`
- Retryable distribution: `{'False': 6}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 10000, 'max_resources': 20000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `4cbc1590-e7eb-4b48-8edf-9e3c2012e0e2` | `NAVIGATION` | - | False | `https://lookaside.fbsbx.com/elementpath/media` |
| 2 | `4cbc1590-e7eb-4b48-8edf-9e3c2012e0e2` | `NAVIGATION` | - | False | `https://lookaside.fbsbx.com/elementpath/media` |
| 3 | `78180fb6-6202-4509-a27b-95a08a1ef30d` | `NAVIGATION` | - | False | `https://lookaside.fbsbx.com/elementpath/media` |
| 4 | `4cbc1590-e7eb-4b48-8edf-9e3c2012e0e2` | `NAVIGATION` | - | False | `https://lookaside.fbsbx.com/elementpath/media` |
| 5 | `d6668c42-6476-49be-9be6-eb0430a67be1` | `NAVIGATION` | - | False | `https://play-lh.googleusercontent.com/X-8he4POOfmlNuZiTgI9KNYRryejpKKPNzvqp1c3LrAQdT7JOBu9dKxLzzpI_aSRIEyQhpnT30w_SlN3YWBBAg=s0-br30=w600-h300-pc0xffffff-pd` |
| 6 | `d6668c42-6476-49be-9be6-eb0430a67be1` | `NAVIGATION` | - | False | `https://play-lh.googleusercontent.com/X-8he4POOfmlNuZiTgI9KNYRryejpKKPNzvqp1c3LrAQdT7JOBu9dKxLzzpI_aSRIEyQhpnT30w_SlN3YWBBAg=s0-br30=w600-h300-pc0xffffff-pd` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
