# `diagnose_crawl_stall`

Chẩn đoán job chạy lâu, queue đứng, budget đã chạm hoặc URL expansion/loop.

Input:

```json
{"job_id": "string", "poll_seconds": 10, "sample_pages": [1, 2, 10]}
```

Tool chỉ poll bounded tối đa 60 giây và không cancel/retry job.
