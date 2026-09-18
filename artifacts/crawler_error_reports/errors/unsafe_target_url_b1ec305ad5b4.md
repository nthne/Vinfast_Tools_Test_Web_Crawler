# Detailed Crawler Error Report

## Error signature: `UNSAFE_TARGET_URL`

**Message:** Download host could not be resolved (add the host to ssrf_allowed_hosts if this is intended)

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

- Status/kind distribution: `{'RESOURCE': 3, 'NAVIGATION': 4}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 7}`
- Retryable distribution: `{'False': 7}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 1200, 'max_resources': 20000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `bd53b4bc-976b-43f6-b9cb-02b9d86b3417` | `RESOURCE` | - | False | `https://www.foody.vn/__get/trace/PhotoCollectionsViewer.gif` |
| 2 | `87c20993-79ec-4f48-8014-4d6fa6013c27` | `RESOURCE` | - | False | `https://visualstudio.microsoft.com/wp-content/uploads/2025/12/circles-66x66.webp` |
| 3 | `f14888c0-5add-4364-8910-812345e7c6c2` | `NAVIGATION` | - | False | `https://www.foody.vn/(A(&amp;amp;%20%20%20%20%20%20%20%20quot;-cpjdosfhwxnr-&amp;amp;%20%20%20%20%20%20%20%20quot;))/bao-mat-thong-tin` |
| 4 | `87c20993-79ec-4f48-8014-4d6fa6013c27` | `RESOURCE` | - | False | `https://visualstudio.microsoft.com/wp-content/uploads/2025/12/circles-66x66.webp` |
| 5 | `106e0812-89d9-4ad5-ada7-5f329f6038cc` | `NAVIGATION` | - | False | `https://down-vn.img.susercontent.com/vn-11134259-7r98o-lwfbxja9reft7a@resize_ss300x300` |
| 6 | `041d922b-85bc-4553-aa4e-bfc5289ce3db` | `NAVIGATION` | - | False | `https://down-vn.img.susercontent.com/vn-11134259-7r98o-lw8bk11b65ztde@resize_ss320x320` |
| 7 | `106e0812-89d9-4ad5-ada7-5f329f6038cc` | `NAVIGATION` | - | False | `https://down-vn.img.susercontent.com/vn-11134259-7r98o-lwfbxja9reft7a@resize_ss300x300` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
