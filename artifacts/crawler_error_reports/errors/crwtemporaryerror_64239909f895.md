# Detailed Crawler Error Report

## Error signature: `CRWTEMPORARYERROR`

**Message:** crw temporary failure retries exhausted: 

## Impact

| Metric | Value |
|---|---:|
| Job ID | `e8e5c6ad-27f8-4585-83d2-ac9423d1cc47` |
| Source ID | `c306f333-5aaa-4325-abea-9ab2c276bdec` |
| Pages with this error in this job | 4 |
| All failed pages in this job | 57 |
| Share of failed pages | 7.0% |
| Generated at (UTC) | `2026-09-18T04:00:26.376890+00:00` |

## Evidence

- Status/kind distribution: `{'NAVIGATION': 3, 'RESOURCE': 1}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 4}`
- Retryable distribution: `{'False': 4}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 1200, 'max_resources': 2000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `4008c7a9-314f-4789-9436-5688c0f8b276` | `NAVIGATION` | - | False | `https://edgedl.me.gvt1.com/android/studio/install/2026.1.4.7/android-studio-quail4-mac_arm.dmg` |
| 2 | `e4fc1cbd-ce6a-446e-a2ac-fa17adb7fc01` | `NAVIGATION` | - | False | `https://edgedl.me.gvt1.com/android/studio/install/2026.1.4.7/android-studio-quail4-mac.dmg` |
| 3 | `6d906e3d-ea6a-4475-8ae2-90221a2f7032` | `NAVIGATION` | - | False | `https://edgedl.me.gvt1.com/android/studio/install/2026.1.4.7/android-studio-quail4-windows.exe` |
| 4 | `3ae39eae-7ef1-4774-865a-36c491e41988` | `RESOURCE` | - | False | `https://edgedl.me.gvt1.com/android/studio/ide-zips/2026.1.4.7/android-studio-quail4-windows.zip` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
