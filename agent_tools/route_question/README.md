# `route_question`

Chọn tool read-only phù hợp với câu hỏi lặp lại của người dùng.

Input:

```json
{"question": "string"}
```

Nếu chưa có capability phù hợp, trả về `tool_proposal` thay vì tự gọi endpoint mutation.

Câu hỏi có URL 404 kèm dấu hiệu `path`, `version`, `crawler` hoặc `document`
sẽ được route sang `diagnose_url_404_mismatch`.
