# Detailed Crawler Error Report

## Error signature: `CRW_PERMANENT`

**Message:** Blocked by anti-bot (generic_block): Access Denied on short page (HTTP 403, 111 bytes)

## Impact

| Metric | Value |
|---|---:|
| Job ID | `d61f29db-0079-46dd-82c5-23a159f8ea17` |
| Source ID | `c306f333-5aaa-4325-abea-9ab2c276bdec` |
| Pages with this error in this job | 5 |
| All failed pages in this job | 87 |
| Share of failed pages | 5.7% |
| Generated at (UTC) | `2026-09-18T04:01:00.995416+00:00` |

## Evidence

- Status/kind distribution: `{'NAVIGATION': 5}`
- HTTP status distribution: `{'NO_HTTP_STATUS': 5}`
- Retryable distribution: `{'False': 5}`
- Runtime crawl config: `{'max_depth': 5, 'max_pages': 10000, 'max_resources': 20000, 'frequency': 'DAILY', 'only_main_content': False, 'render_js': None, 'wait_for_ms': None, 'timeout_ms': None}`

## Affected pages

| # | Page ID | Kind | HTTP status | Retryable | URL |
|---:|---|---|---:|---|---|
| 1 | `292bc50e-f2d1-4df3-9113-595dcad52d71` | `NAVIGATION` | - | False | `https://kstatic.googleusercontent.com/files/13f3dceecb5cacec50c4d2d8cc57f9b100eac82b852c26114583769a33acc184dbf9b63f285b04877aa2d3e3df2e239a68afede062bed819ad15676cf78e2b95=w1080` |
| 2 | `292bc50e-f2d1-4df3-9113-595dcad52d71` | `NAVIGATION` | - | False | `https://kstatic.googleusercontent.com/files/13f3dceecb5cacec50c4d2d8cc57f9b100eac82b852c26114583769a33acc184dbf9b63f285b04877aa2d3e3df2e239a68afede062bed819ad15676cf78e2b95=w1080` |
| 3 | `fe88d007-9e27-413b-8739-b12041d42178` | `NAVIGATION` | - | False | `https://kstatic.googleusercontent.com/files/bb8c4feb3f60e5ded6188fa0094434f6d812715250bd4e172c43e961b666957c3b9c8436757ca4c8390a502bd1eb608ca9f90801bbb3ee8f1cbaca2b3bbeb7c3=w1080` |
| 4 | `37110b40-46c5-4209-969e-388df7eb5a4d` | `NAVIGATION` | - | False | `https://kstatic.googleusercontent.com/files/9f925480768b376d3c64814791ca9ecd4ca6bc0326b3a531101fc7f2c20ce4cbe799d60fca39e537f2ca1b49e9ad6f80ea768bf197376540d1477948a9cd6a2d=w1080` |
| 5 | `292bc50e-f2d1-4df3-9113-595dcad52d71` | `NAVIGATION` | - | False | `https://kstatic.googleusercontent.com/files/13f3dceecb5cacec50c4d2d8cc57f9b100eac82b852c26114583769a33acc184dbf9b63f285b04877aa2d3e3df2e239a68afede062bed819ad15676cf78e2b95=w1080` |

## Recommended checks

1. Correlate this error message with crawler worker logs at the job timestamp.
2. Check whether the failure occurred before an HTTP response was recorded.
3. Verify retryability and whether the error was incorrectly marked permanent.
4. Reproduce with one page before starting a full recrawl.

## Safety

- URLs omit query strings and fragments.
- This report was generated from read-only crawler API calls.
- No retry, cancel, delete, or crawler configuration mutation was performed.
