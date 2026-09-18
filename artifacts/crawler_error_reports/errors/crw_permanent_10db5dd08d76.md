# Detailed Crawler Error Report

## Error signature: `CRW_PERMANENT`

**Message:** No usable content could be extracted (Structural: minimal_text on small page (1485 bytes, 14 chars visible))

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

- Status/kind distribution: `{'NAVIGATION': 1}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 1}`
- Retryable distribution: `{'False': 1}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 1200, 'max_resources': 20000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `0b08e63e-4b0c-4639-aff5-6d49370519e9` | `NAVIGATION` | - | False | `https://goo.gle/3xj0b2F` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
