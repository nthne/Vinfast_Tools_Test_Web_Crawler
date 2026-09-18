# Detailed Crawler Error Report

## Error signature: `CRWTEMPORARYERROR`

**Message:** crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: No JS renderer available

## Impact

| Metric | Value |
|---|---:|
| Job ID | `49ddbae0-3320-4d15-9ffa-eeaf69099d68` |
| Source ID | `c306f333-5aaa-4325-abea-9ab2c276bdec` |
| Pages with this error in this job | 5 |
| All failed pages in this job | 592 |
| Share of failed pages | 0.8% |
| Generated at (UTC) | `2026-09-18T05:01:40.972729+00:00` |

## Evidence

- Status/kind distribution: `{'RESOURCE': 5}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 5}`
- Retryable distribution: `{'False': 5}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 1200, 'max_resources': 20000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `f8c39d0b-3b9b-4a8d-a956-1b5b2fa93caf` | `RESOURCE` | - | False | `https://services.google.com/fh/files/misc/assured_controls_in_google_workspace_ebook.pdf` |
| 2 | `683e3de0-5aed-4619-bf92-ecf59a44afaa` | `RESOURCE` | - | False | `https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip` |
| 3 | `4f9056ba-afdc-4f31-ab36-7edec3cd9e54` | `RESOURCE` | - | False | `https://dl.google.com/android/repository/commandlinetools-win-15859902_latest.zip` |
| 4 | `683e3de0-5aed-4619-bf92-ecf59a44afaa` | `RESOURCE` | - | False | `https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip` |
| 5 | `f8c39d0b-3b9b-4a8d-a956-1b5b2fa93caf` | `RESOURCE` | - | False | `https://services.google.com/fh/files/misc/assured_controls_in_google_workspace_ebook.pdf` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
