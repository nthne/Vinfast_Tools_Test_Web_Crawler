# Detailed Crawler Error Report

## Error signature: `CRWTEMPORARYERROR`

**Message:** crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP discovery failed: error sending request

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

- Status/kind distribution: `{'RESOURCE': 3, 'NAVIGATION': 2}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 5}`
- Retryable distribution: `{'False': 5}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 1200, 'max_resources': 20000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `ca0d303a-ee01-45a4-8a81-ce26d2274d2a` | `RESOURCE` | - | False | `https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjEDNPQqJo401AgWeMJYr-5hM9BJoO_AyYLRhgeI1XvCHonCGXVpgNnUquEwLiJwZMjVsdRvnEkQQgwzISNhXPTNN5TB3gyCsjyUYtvlxKV_Q9akEUK8LoXtTSvA6tEIKqn30uUrpy7HL3Uet7-itOc5imUx8Hy-1AuRSHnHf1y8EmD5jAK81620GGKPCg/s16000/Move%20from%20conversation%20to%20creation%20with%20file%20generation%20in%20Gemini.gif` |
| 2 | `8f180e83-8367-4e3f-81e1-793ceede284f` | `RESOURCE` | - | False | `https://www.lookout.com/documents/datasheets/us/lookout-google-cloud-integration-ds-us.pdf` |
| 3 | `dea7e74b-b92c-43be-9a1d-6b19ae080179` | `NAVIGATION` | - | False | `https://stackoverflow.com/questions/tagged/google-apps-script` |
| 4 | `22c05fd4-5088-4f83-89a2-02f6619a2329` | `RESOURCE` | - | False | `https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEigpAe5S6F6l2cYRgnt99eTKRVJ-OzbZk28fj_sg0oEVrd_QjarhIW94eohIccCt-e0uTrJ2L2DhyphenhyphenqethzUxtppZStoKMZdXPbkRdCBhSJBuWY-Ak8ybFEo3NKdeqLClHWqCrbRdQInb-hx0Wg7LfG5ryAozqfJirNMMnoz3s75bu6EwJrGZzkh43LX-a0/s1600/6266.gif` |
| 5 | `983e9146-f1ed-4355-99fa-fa5cffc8180a` | `NAVIGATION` | - | False | `https://foodypos.vn/` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
