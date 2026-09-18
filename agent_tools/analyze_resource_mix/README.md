# `analyze_resource_mix`

Phân tích vì sao crawl thu thập nhiều resource như ảnh, CSS, JavaScript hoặc HTML.

Input:

```json
{"job_id": "string", "sample_pages": 8, "page_size": 100}
```

Tool thống kê kind, MIME, route, host ngoài, URL dài/lặp path và không thay đổi allowlist.
