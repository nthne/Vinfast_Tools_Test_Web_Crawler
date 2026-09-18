# `audit_crawl_history`

Audits historical crawl jobs for selected sources and date ranges. It produces
a natural-language Markdown report explaining whether each failure is caused
by crawler infrastructure, upstream access/anti-bot, SSRF/DNS policy,
extraction, download status, or URL expansion.

Example input:

```json
{
  "source_keywords": ["foody", "pytorch"],
  "start_date": "2026-09-16",
  "end_date": "2026-09-17",
  "include_cancelled": true
}
```

The tool is read-only and uses page metadata only; it does not retry, cancel,
update, or delete crawler jobs.
