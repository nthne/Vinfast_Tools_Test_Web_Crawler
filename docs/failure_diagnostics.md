# Failure diagnostics

## `diagnose_failed_pages`

Đây là read-only tool dùng khi nhiều page cùng `FAILED`, đặc biệt với thông báo UI như `The system gave up`.

Tool đối chiếu:

- job status và runtime config;
- page status/kind;
- `failure` và `metadata.error`;
- error code/message/retryable;
- HTTP status và final URL;
- tỷ lệ lỗi theo navigation/resource;
- dấu hiệu `js_escalation_failed`, `CDP`, `WS closed`, hoặc lỗi renderer.

Tool phân biệt các nhóm:

```text
NO_FAILURES
RENDERER_INFRASTRUCTURE_FAILURE
HTTP_FAILURE
SYSTEMIC_FAILURE
MIXED_FAILURE
```

Nếu page failed nhưng không có HTTP status, không được kết luận website trả 4xx/5xx. Đây thường là lỗi trước bước nhận response, ví dụ browser renderer/CDP.

Tool không retry, không sửa job, không cancel và không thay đổi source config.
