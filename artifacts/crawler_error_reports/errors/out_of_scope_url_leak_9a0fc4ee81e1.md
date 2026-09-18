# Detailed Crawler Diagnostic Report

## Finding: `OUT_OF_SCOPE_URL_LEAK`

**Message:** Foody job contains external page/resource URLs outside foody.vn; asset URLs returned HTML and exposed external links that could expand the crawl queue.

## Impact

This is a crawler QA diagnostic finding. It is reported separately from page-failure counts.

| Metric | Value |
|---|---|
| `job_id` | `49ddbae0-3320-4d15-9ffa-eeaf69099d68` |
| `scope_domains` | `['foody.vn']` |
| `sample_count` | `5000` |
| `out_of_scope_page_count` | `5000` |
| `out_of_scope_link_count` | `12885` |
| `html_resource_with_links_count` | `4854` |
| `asset_url_returning_html_count` | `4854` |
| `url_path_expansion_count` | `5000` |
| `finding_code` | `OUT_OF_SCOPE_URL_LEAK` |
| `mismatch_count` | `1` |

## Observed evidence

### Observation 1

- `scope_domains`: `['foody.vn']`
- `sample_count`: `5000`
- `out_of_scope_page_count`: `5000`
- `out_of_scope_link_count`: `12885`

### Observation 2

- `external_domains`: `{'domains.google.com': 3873, 'answers.microsoft.com': 1127}`
- `html_resource_with_links_count`: `4854`
- `asset_url_returning_html_count`: `4854`
- `url_path_expansion_count`: `5000`

### Observation 3

- `url`: `https://answers.microsoft.com/en-us/media/qna/hero/media/.../logo-entra.png`
- `title`: `Microsoft Q&A \| Microsoft Learn`
- `kind`: `RESOURCE`
- `content_type`: `text/html`
- `warning`: `redirected_to: https://learn.microsoft.com/en-us/answers/`

### Observation 4

- `out_of_scope_links`: `['https://go.microsoft.com/fwlink/p?LinkID=2092881', 'https://support.microsoft.com/en-us/teams', 'https://abs.twimg.com/favicons/twitter.3.ico']`

## Recommended actions

1. Enforce the source host allowlist before enqueueing NAVIGATION URLs.
2. Do not extract or follow links from RESOURCE responses that return HTML.
3. Keep page and resource budgets separate and canonicalize repeated URL paths.

## Safety

- This finding was recorded from read-only crawler/API and upstream probes.
- Query strings and fragments are omitted from URL evidence.
- No retry, cancel, delete, or crawler configuration mutation was performed.
- Generated at (UTC): `2026-09-18T05:01:40.972729+00:00`
