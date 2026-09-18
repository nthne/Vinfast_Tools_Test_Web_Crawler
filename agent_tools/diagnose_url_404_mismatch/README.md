# `diagnose_url_404_mismatch`

Checks whether a crawler URL returns 404 because the crawler retained an old,
unversioned, or otherwise stale document path while the current upstream URL
is valid.

Input:

```json
{
  "job_id": "crawl-job-id",
  "expected_url": "https://docs.pytorch.org/docs/2.14/utils.html",
  "sample_pages": null,
  "max_probes": 20,
  "request_timeout": 15
}
```

The tool reads pages from the crawler, probes the expected URL and matching
crawler candidates, and returns evidence for:

- `CRAWLER_URL_VERSION_MISMATCH`;
- `UPSTREAM_404_CONFIRMED`;
- `NO_MATCHING_CRAWLER_PAGE`;
- `NO_404_MISMATCH_OBSERVED`.

It is read-only. It does not retry, update, cancel, or delete crawler data.
Query strings and fragments are removed from returned evidence.
