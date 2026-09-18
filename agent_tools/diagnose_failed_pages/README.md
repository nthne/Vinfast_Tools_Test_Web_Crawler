# `diagnose_failed_pages`

Phân biệt lỗi HTTP/site với lỗi renderer/CDP khi nhiều page cùng failed hoặc UI hiển thị `The system gave up`.

Input:

```json
{"job_id": "string", "sample_pages": null}
```

Tool kiểm tra failure/error, retryable, HTTP status, kind, renderer signature và failure rate. Tool không retry, cancel hoặc sửa config.
