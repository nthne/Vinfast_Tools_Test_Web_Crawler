# Detailed Crawler Error Report

## Error signature: `CRW_PERMANENT`

**Message:** Blocked by anti-bot (generic_block): HTTP 403 with near-empty response (21 bytes)

## Impact

| Metric | Value |
|---|---:|
| Job ID | `e8e5c6ad-27f8-4585-83d2-ac9423d1cc47` |
| Source ID | `c306f333-5aaa-4325-abea-9ab2c276bdec` |
| Pages with this error in this job | 1 |
| All failed pages in this job | 57 |
| Share of failed pages | 1.8% |
| Generated at (UTC) | `2026-09-18T04:00:26.376890+00:00` |

## Evidence

- Status/kind distribution: `{'RESOURCE': 1}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 1}`
- Retryable distribution: `{'False': 1}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 1200, 'max_resources': 2000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `ee4f0671-a745-4ba2-8bdf-6603a421a300` | `RESOURCE` | - | False | `https://scontent-lax3-1.xx.fbcdn.net/v/t39.2365-6/457477312_480861821467896_777041002100550877_n.pdf` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
