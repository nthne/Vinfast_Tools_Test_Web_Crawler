# Detailed Crawler Error Report

## Error signature: `UNSAFEDOWNLOADURL`

**Message:** Connected peer differs from the validated DNS result

## Impact

| Metric | Value |
|---|---:|
| Job ID | `49ddbae0-3320-4d15-9ffa-eeaf69099d68` |
| Source ID | `c306f333-5aaa-4325-abea-9ab2c276bdec` |
| Pages with this error in this job | 7 |
| All failed pages in this job | 592 |
| Share of failed pages | 1.2% |
| Generated at (UTC) | `2026-09-18T05:01:40.972729+00:00` |

## Evidence

- Status/kind distribution: `{'RESOURCE': 7}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 7}`
- Retryable distribution: `{'False': 7}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 1200, 'max_resources': 20000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `4e24584c-db18-498d-97b4-a38edf865110` | `RESOURCE` | - | False | `https://support.microsoft.com/images/error-page.webp` |
| 2 | `133978a0-79d4-4a1f-a407-e4baa7990c7d` | `RESOURCE` | - | False | `https://support.microsoft.com/favicon-32x32.png` |
| 3 | `41a5daa2-04ca-42e0-9ace-5a86cdefdd4e` | `RESOURCE` | - | False | `https://www.googlecloudcommunity.com/user_avatar/discuss.google.dev/nathan_list/25/186597_2.png` |
| 4 | `133978a0-79d4-4a1f-a407-e4baa7990c7d` | `RESOURCE` | - | False | `https://support.microsoft.com/favicon-32x32.png` |
| 5 | `133978a0-79d4-4a1f-a407-e4baa7990c7d` | `RESOURCE` | - | False | `https://support.microsoft.com/favicon-32x32.png` |
| 6 | `41a5daa2-04ca-42e0-9ace-5a86cdefdd4e` | `RESOURCE` | - | False | `https://www.googlecloudcommunity.com/user_avatar/discuss.google.dev/nathan_list/25/186597_2.png` |
| 7 | `c4bb57d8-960d-48f7-9d0b-4ca581e1d57b` | `RESOURCE` | - | False | `https://developers.google.com/static/business-communications/rcs-business-messaging/images/security-docs_72.png` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
