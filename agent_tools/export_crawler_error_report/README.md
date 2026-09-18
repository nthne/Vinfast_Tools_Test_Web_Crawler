# `export_crawler_error_report`

Gom các lỗi của một crawl job thành các report Markdown dễ đọc và dễ gửi cho đội phát triển crawler.

Mặc định ghi vào:

```text
artifacts/crawler_error_reports/errors/<error_code>_<signature>.md
artifacts/crawler_error_reports/crawler_error_summary.md
```

Input:

```json
{
  "job_id": "string",
  "output_path": "optional/path/report.md",
  "output_dir": "optional/report/directory",
  "summary_path": "optional/path/crawler_error_summary.md",
  "diagnostic_findings": [],
  "sample_pages": null,
  "max_page_rows": 200
}
```

Mỗi error signature (error code + message) có một detail report riêng gồm:

- impact và tỷ lệ của error;
- status/kind/HTTP/retryable evidence;
- runtime config;
- toàn bộ page bị ảnh hưởng;
- các bước kiểm tra đề xuất.

Ngoài ra, `crawler_error_summary.md` gồm:

- thống kê ngắn gọn theo error type;
- tổng số page lỗi và số job bị ảnh hưởng;
- danh sách crawl job đã ghi nhận;
- link tới detail report tương ứng.

Diagnostic findings như `SOURCE_URL_MISSING_TRAILING_SLASH` được ghi ở mục
`Additional QA findings` và có detail report riêng. Các finding này không làm
tăng giả số page failed.

URL trong report bị loại query string và fragment để tránh lộ signed URL/token. Tool chỉ ghi file local, không retry/cancel/update crawler job.
