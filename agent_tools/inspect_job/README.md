# `inspect_job`

Đọc trạng thái, counter, timestamp và runtime crawl config của một job.

Input:

```json
{"job_id": "string", "sample_pages": 0}
```

Tool tính `effective_record_budget = max_pages + max_resources` khi upstream cung cấp đủ hai giá trị.
