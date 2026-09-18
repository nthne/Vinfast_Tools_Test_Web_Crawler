# Vin Auto Crawl — chức năng, properties và đề xuất QA

Audit read-only ngày 2026-09-16 trên `https://vin-auto-crawl.hotavn.com/`, bằng HTML/JavaScript public và `/openapi.json`. Không gửi login request và không đọc dữ liệu protected vì chưa có credential.

## 1. Auth và quyền

### Frontend/API quan sát được

- UI routes: `/auth/login`, `/auth/register`, `/auth/forgot-password`, `/auth/reset-password`, `/auth/verify-email`.
- Login: `POST /api-non/v1.0/users/login`, body `{email, password}`.
- Refresh: `POST /api-non/v1.0/users/refresh-token`, body `{refresh_token}`.
- Setup: `GET /api-non/v1.0/users/setup-status` — public, hiện trả `first_time_setup`, `has_admin_user`, `registration_enabled`, `forgot_password_enabled`, `email_verification_enabled`.
- User profile: `GET /api/v1.0/user/get`.
- Allowed endpoint permissions: `GET /api-non/v1.0/system/list-endpoint-allow`.
- Frontend lưu session/token bằng cookie; auth request gửi `Authorization: Bearer <token>` và `x-token: <token>`.
- OpenAPI cũng khai báo API-key scheme `api-key`; cần kiểm tra credential thực tế có dùng header này hay không trước khi bật adapter.

### Properties trả về từ login

`user_id`, `email`, `full_name`, `permission`, `is_email_verified`, `token`, `refresh_token`, `token_type`, `expired_at`, `refresh_token_expired_at`.

### QA nên check

| Error code đề xuất | Severity | Bằng chứng / ý nghĩa |
|---|---:|---|
| `AUTH_FAILED` | CRITICAL | Login HTTP/error body; không lưu password. |
| `AUTH_TOKEN_MISSING` | CRITICAL | Login success nhưng thiếu `token` hoặc token type. |
| `AUTH_SESSION_EXPIRED` | ERROR | Token hết hạn, refresh fail, hoặc batch sau trả 401/login page. |
| `AUTH_EMAIL_NOT_VERIFIED` | ERROR | `is_email_verified=false`; frontend sẽ logout/đưa tới unauthorized. |
| `AUTH_PERMISSION_DENIED` | ERROR | 403 hoặc permission không cho phép crawl read. |
| `AUTH_ENDPOINT_NOT_ALLOWED` | ERROR | API trả danh sách allowed endpoints không bao gồm endpoint QA cần đọc. |
| `AUTH_COOKIE_OR_TOKEN_MISMATCH` | ERROR | Một kiểu auth thành công nhưng kiểu header/cookie còn lại không truy cập được. |
| `AUTH_SECRET_LEAK` | CRITICAL | Token/password/cookie xuất hiện trong log, report, UI, URL hoặc export. |
| `UPSTREAM_HEALTH_DEGRADED` | WARNING | `GET /api/v1.0/status` không trả `{status: "ok", service: "api"}`. |

## 2. Dashboard / overview

UI gọi song song:

- `listSources({page, page_size})` và filter `enabled`, `domain`.
- `listJobs({page, page_size, status})`.
- `listPages({page, page_size, status:[...]})`.
- `listDomains()`.
- `runSource(source_id)` từ action “Run now”.
- Poll job đang chạy mỗi 5 giây.

Properties chính trên overview: số source, source enabled, job running/failed, tổng page, page `NEW_INFO`, domain count, top recent sources/jobs.

### QA nên check

- `OVERVIEW_COUNT_MISMATCH`: total trên overview khác total từ endpoint phân trang.
- `PAGINATION_TOTAL_INVALID`: `total < items`, `page/page_size` không hợp lệ, trang cuối lặp item.
- `PAGINATION_DUPLICATE_PAGE`: các trang API trả trùng cùng identifier.
- `JOB_STATUS_STALE`: job RUNNING/PENDING không thay đổi sau thời gian ngưỡng.
- `RUN_DUPLICATE_TRIGGER`: không gửi; QA chỉ quan sát event/run result nếu người dùng chủ động chạy source.

## 3. Sources

### Functions và endpoint

| Function UI | HTTP | Properties/params |
|---|---|---|
| `listSources` | `GET /api/v1.0/crawl/sources` | `page`, `page_size`, `enabled`, `domain`; envelope `items,total,page,page_size`. |
| `getSource` | `GET /api/v1.0/crawl/sources/{source_id}` | source detail. |
| `createSource` | `POST /api/v1.0/crawl/sources` | `url`, `display_name`, `domain?`, `enabled?`, `crawl_config?`, `rules?`. |
| `updateSource` | `PATCH /api/v1.0/crawl/sources/{source_id}` | partial source update. |
| `bulkCreateSources` | `POST /api/v1.0/crawl/sources/bulk` | `{items: [...]}`. |
| `runSource` | `POST /api/v1.0/crawl/sources/{source_id}/run` | queues an immediate crawl job. |
| `deleteSource` | `DELETE /api/v1.0/crawl/sources/{source_id}` | destructive; QA tool must not call. |

### `SourceResponse`

`id`, `url`, `display_name`, `domain`, `enabled`, `crawl_config`, `rules`, `next_run_at`, `created_at`, `updated_at`, `degraded[]`.

### `CrawlConfig`

`max_depth` (0–1,000,000; default 3), `max_pages` (>=1; default 10,000), `max_resources` (>=0; default 20,000), `frequency` (`HOURLY|EVERY_6_HOURS|DAILY|WEEKLY|MONTHLY`), `only_main_content`, `render_js` (nullable auto/boolean), `wait_for_ms` (nullable), `timeout_ms` (nullable).

### `CrawlRules` / `UrlFilterRule`

`rules_filter_url[]`; each rule has `group_resource_apply[]`, `content_type_apply[]`, `type_filter` (`INCLUDE|EXCLUDE`), and non-empty regex `rule_context`.

### QA nên check

- `SOURCE_MISSING_REQUIRED_FIELD`: id/url/display_name/domain/crawl_config/rules/timestamps.
- `SOURCE_INVALID_URL`, `SOURCE_DOMAIN_MISMATCH`: seed URL parse được và domain khớp canonical domain.
- `SOURCE_DUPLICATE_SEED`: source khác nhau trùng canonical seed/domain.
- `SOURCE_INVALID_SCHEDULE`: frequency ngoài enum hoặc next_run_at không hợp lệ/future bất thường.
- `SOURCE_CONFIG_INVALID`: max depth/pages/resources sai range hoặc kiểu.
- `SOURCE_RENDER_CONFIG_INCONSISTENT`: `wait_for_ms >= timeout_ms`, wait được đặt nhưng render JS false, hoặc timeout quá nhỏ.
- `SOURCE_RULE_INVALID_REGEX`: regex không compile hoặc rule không áp dụng cho page/resource/content route nào.
- `SOURCE_RULE_CONTRADICTION`: cùng URL bị include và exclude ở rule có precedence không giải thích được.
- `SOURCE_DEGRADED`: `degraded[]` không rỗng; hiển thị rõ field nào bị fallback.
- `SOURCE_UPDATED_AFTER_CRAWL`: source update timestamp sau job nhưng job không ghi snapshot config.

## 4. Jobs

### Functions và endpoint

- `listJobs`: `GET /api/v1.0/crawl/jobs?page&page_size&source_id&status&domain`.
- `getJob`: `GET /api/v1.0/crawl/jobs/{job_id}`.
- `cancelJob`: `POST /api/v1.0/crawl/jobs/{job_id}/cancel`; destructive/control action, QA tool chỉ GET.

### `JobResponse`

`id`, `source_id`, `domain`, `status` (`PENDING|RUNNING|COMPLETED|FAILED|CANCELLED`), `started_at`, `finished_at`, `crawl_config`, `metadata`, `created_at`, `updated_at`, `degraded[]`.

### `CrawlJobMetadata`

`total_pages`, `in_queue_count`, `success_count`, `unchanged_count`, `failed_count`, `skipped_count`, `error_summary[]`.

### QA nên check

- `JOB_INVALID_STATUS`, `JOB_INVALID_TRANSITION`: status không thuộc enum hoặc regression transition.
- `JOB_TIME_INVALID`: finished trước started, timestamp future, duration âm, RUNNING nhưng không có started.
- `JOB_COUNTER_NEGATIVE`: counter âm.
- `JOB_COUNTER_INCONSISTENT`: `in_queue_count > total_pages`, hoặc tổng finalized vượt total.
- `JOB_PAGE_COUNT_MISMATCH`: job metadata khác page endpoint theo job.
- `JOB_SOURCE_MISMATCH`: job source/domain khác source record hoặc page domain.
- `JOB_TERMINAL_WITHOUT_FINISH`: COMPLETED/FAILED/CANCELLED nhưng thiếu finished_at.
- `JOB_FAILED_WITHOUT_DIAGNOSTIC`: FAILED nhưng không có `error_summary`/page failure evidence.
- `JOB_ERROR_SUMMARY_MISMATCH`: error summary không khớp phân bố `PageFailure`.
- `JOB_CONFIG_SNAPSHOT_DRIFT`: crawl_config của job thay đổi so với config snapshot tại lúc run.
- `JOB_DEGRADED`: `degraded[]` không rỗng.

## 5. Pages/content

### Functions và endpoint

| Function | HTTP | Properties/params |
|---|---|---|
| `listPages` | `GET /api/v1.0/crawl/pages` | `page`, `page_size`, `job_id`, `status[]`, `kind[]`, `domain`; envelope `items,total,page,page_size`. |
| `getPage` | `GET /api/v1.0/crawl/pages/{page_id}` | metadata record. |
| `viewPage` | `GET /api/v1.0/crawl/pages/{page_id}/view` | rendered/stored markdown, assets, or signed download URL. |
| `getPageDownload` | `GET /api/v1.0/crawl/pages/{page_id}/download?raw=bool` | signed URL for processed/raw object. |
| `previewClean` | `GET /api/v1.0/crawl/pages/{page_id}/clean-preview?clean_mode&scope` | page/source clean evidence. |
| `listDomains` | `GET /api/v1.0/crawl/pages/domains` | domain and page_count. |
| `getLinkMap` | `GET /api/v1.0/crawl/pages/link-map?domain&max_pages&max_nodes` | bounded nodes/edges graph. |

### `CrawlPageResponse`

`id`, `crawl_job_id`, `url`, `domain`, `source_hash`, `content_type`, `s3_key`, `raw_s3_key`, `links_s3_key`, `retry_count`, `depth`, `kind` (`NAVIGATION|RESOURCE`), `status` (`IN_QUEUE|NEW_INFO|SKIPPED|SKIPPED_ROBOTS|SKIPPED_RULES|FAILED|CANCELLED`), `ref_crawl_page_id`, `proxy_id`, `metadata`, `failure`, `created_at`, `updated_at`, `degraded[]`.

### `CrawlPageMetadata`

`links[]`, `links_truncated`, `title`, `status_code`, `final_url`, `warnings[]`, `content_route` (`HTML_MARKDOWN|PDF_TEXT|PDF_SCAN|IMAGE|BINARY`), `pdf_scanned`, `skip_reason`, `reused_from_source`, `error`.

### `PageFailure`

`code`, `detail`, `category` (`BLOCKED|NETWORK|TARGET_ERROR|LIMIT|BLOCKED_BY_SAFETY|INTERNAL|NO_CONTENT|UNKNOWN`), `retryable`, `http_status`, `block_reason`.

### `PageViewResponse`

`crawl_page_id`, `url`, `content_type`, `markdown`, `download_url`, `assets[]`, `truncated`.

### QA nên check — MVP/P0

- `MISSING_REQUIRED_FIELD`, `INVALID_STATUS_CODE`, `EMPTY_URL`, `INVALID_URL`.
- `PAGE_JOB_SOURCE_MISMATCH`, `PAGE_DOMAIN_MISMATCH`, `PAGE_DEPTH_EXCEEDS_CONFIG`.
- `PAGE_STATUS_FAILURE_WITHOUT_FAILURE`, `PAGE_FAILURE_WITHOUT_FAILED_STATUS`.
- `PAGE_RETRY_COUNT_INVALID`, `PAGE_HASH_MISSING_OR_MALFORMED`.
- `HTTP_404`, `HTTP_429`, `HTTP_5XX`.
- `AUTH_REDIRECT_TO_LOGIN`, `AUTH_LOGIN_PAGE_RETURNED`.
- `EMPTY_PAGE`, `VERY_LOW_CONTENT`, `SOFT_404`.
- `CAPTCHA_PAGE`, `ANTI_BOT_PAGE`.
- `ENCODING_MOJIBAKE`, `UNICODE_REPLACEMENT_CHAR`.
- `CLEAN_RESULT_EMPTY`, `CLEANING_OVER_AGGRESSIVE`.
- `EXACT_DUPLICATE_CONTENT` và đối chiếu `source_hash`/`ref_crawl_page_id`.

### QA nên check — P1 theo properties mới phát hiện

- `CONTENT_ROUTE_MISMATCH`: `content_route`, `content_type`, extension URL và actual returned content không khớp.
- `HTML_EXPECTED_BUT_BINARY`, `PDF_TRUNCATED`, `IMAGE_WITHOUT_OBJECT_KEY`.
- `FINAL_URL_INVALID`, `FINAL_URL_DOMAIN_ESCAPE`: final URL parse lỗi hoặc ra ngoài source domain khi policy không cho phép.
- `REDIRECT_LOOP`, `TOO_MANY_REDIRECTS`: chỉ bật khi upstream cung cấp chain/count; không suy đoán từ final URL đơn lẻ.
- `JS_RENDER_REQUIRED`: HTML/raw object có bundle nhưng markdown/text gần rỗng; so sánh raw/rendered khi có cả hai.
- `PAGE_WARNING_UNEXPLAINED`: metadata warnings hoặc failure code không có recommended action mapping.
- `PAGE_VIEW_ID_URL_MISMATCH`: `crawl_page_id`/URL trong view khác metadata page.
- `PAGE_VIEW_EMPTY`: view 200 nhưng markdown và download_url đều rỗng.
- `PAGE_VIEW_TRUNCATED`: `truncated=true`; không coi là lỗi nếu size limit được cấu hình, nhưng phải flag cho downstream.
- `SIGNED_DOWNLOAD_INVALID`: URL ký hết hạn, content-length/content-type không đúng hoặc download không đọc được.
- `ASSET_REFERENCE_BROKEN`: asset URL không tải được hoặc asset trỏ ra ngoài policy.

## 6. Cleaning và clean modes

UI gọi `listCleanModes()` và dùng `previewClean(page_id, clean_mode, scope)`. Enum mode là `RAW|LIGHT|HEAVY|SAFE`; scope là `PAGE|SOURCE`.

`PageCleanPreview` có `crawl_page_id`, `url`, `clean_mode`, `scope`, `matches_export`, `markdown`, `original_characters`, `kept_characters`, `reverted`, `degraded[]`.

### QA nên check

- `CLEAN_MODE_UNKNOWN`, `CLEAN_SCOPE_UNKNOWN`.
- `CLEAN_CHAR_COUNT_INVALID`: kept/original âm hoặc kept > original.
- `CLEAN_RETENTION_OUTLIER`: retention khác biệt lớn so với source profile.
- `CLEAN_PREVIEW_EXPORT_MISMATCH`: `matches_export=false` ở cùng mode/scope.
- `CLEAN_REVERTED_UNEXPLAINED`: reverted=true nhưng không có evidence/degraded reason.
- `CLEAN_LLM_REQUIRED_UNAVAILABLE`: mode yêu cầu LLM nhưng catalog `llm_ready=false`.
- `CLEAN_MODE_NONDETERMINISTIC`: cùng page/mode trả kết quả hash khác nhau trong cùng job.

## 7. Link graph

`LinkMapResponse`: `domain`, `nodes[]`, `edges[]`, `truncated`.

- Node: `id`, `label`, `page_count`.
- Edge: `source`, `target`, `weight`.

### QA nên check

- `LINK_MAP_ORPHAN_EDGE`: edge source/target không tồn tại trong nodes.
- `LINK_MAP_INVALID_WEIGHT`: weight <= 0.
- `LINK_MAP_PAGE_COUNT_INVALID`: page_count âm hoặc tổng vượt bound.
- `LINK_MAP_DOMAIN_LEAK`: graph domain filter chứa domain ngoài scope.
- `LINK_MAP_LIMIT_IGNORED`: max_pages/max_nodes vượt limit nhưng truncated=false.
- `LINK_MAP_TRUNCATION_UNLABELED`: result bị cắt nhưng truncated không phản ánh.

## 8. Exports/imports

### Functions và endpoint

- `listExports`: `GET /api/v1.0/crawl/exports?page&page_size`.
- `createExport`: `POST /api/v1.0/crawl/exports`.
- `getExportDownload`: `GET /api/v1.0/crawl/exports/{export_id}/download`.
- `downloadTemplate(table)`: `GET /api/v1.0/crawl/exports/templates/{table}`.
- `createUploadTicket(filename, expires_seconds)`: `POST /api/v1.0/crawl/exports/uploads`.
- Browser upload: PUT vào `upload_url`, sau đó `startImport(table, s3_key)` → `POST /api/v1.0/crawl/exports/imports`.
- `bulkDelete(table, payload)`: POST destructive, QA tool không gọi.

### `ExportParams` / `ExportResponse`

Params: `source_ids[]`, `started_from`, `started_to`, `max_rows` (1–1,000,000; default 100,000), `columns` (`SIMPLE|ALL`), `domain`, `url_regex`, `clean_mode`, `upload_s3_key`.

Response: `id`, `type` (`PARQUET_ZIP|SOURCE_TABLE|PROXY_TABLE|SOURCE_IMPORT|PROXY_IMPORT`), `params`, `status` (`PENDING|RUNNING|COMPLETED|FAILED`), `s3_key`, `error`, `row_count`, `cleaning`, `started_at`, `finished_at`, `created_at`, `updated_at`, `degraded[]`.

### QA nên check

- `EXPORT_FILTER_INVALID`: source_ids không tồn tại, date range đảo, max_rows sai, URL regex không compile.
- `EXPORT_STATUS_INVALID`, `EXPORT_TERMINAL_WITHOUT_FINISH`.
- `EXPORT_ROW_COUNT_MISMATCH`: row_count khác số page match filter, có giải thích do truncation/skip.
- `EXPORT_FILTER_LEAK`: row ngoài source/domain/date/url_regex xuất hiện.
- `EXPORT_SCHEMA_DRIFT`: SIMPLE/ALL thiếu hoặc thêm field bất ngờ.
- `EXPORT_CONTENT_HASH_MISMATCH`: export content khác page/view hash ngoài cleaning mode.
- `EXPORT_CLEANING_REGRESSION`: cleaning metrics (`characters_before/after`, `reverted_pages`, `degraded`) xấu hơn baseline.
- `EXPORT_DOWNLOAD_INVALID`, `EXPORT_DOWNLOAD_EXPIRED`, `EXPORT_ARCHIVE_CORRUPT`.
- `IMPORT_TEMPLATE_SCHEMA_INVALID`, `IMPORT_ROW_ERROR_UNEXPECTED`, `IMPORT_DUPLICATE_KEY`.
- `UPLOAD_TICKET_EXPIRED`, `UPLOAD_CONTENT_TYPE_MISMATCH`.

## 9. Domain policies và proxies

### Functions/endpoints

- `listDomainPolicies`: `GET /api/v1.0/crawl/domain-policies`.
- `upsertDomainPolicy(domain, payload)`: `PUT /api/v1.0/crawl/domain-policies/{domain}`.
- `deleteDomainPolicy(domain)`: `DELETE …/{domain}`; destructive.
- `listProxies`: `GET /api/v1.0/crawl/proxies`.
- `createProxy`: `POST /api/v1.0/crawl/proxies`.
- `updateProxy`: `PATCH /api/v1.0/crawl/proxies/{proxy_id}?revive=bool`.
- `deleteProxy`: `DELETE /api/v1.0/crawl/proxies/{proxy_id}`; destructive.

### Properties

Domain policy: `domain`, `rps > 0`, `burst >= 1`, `max_concurrent >= 1`, `proxy_strategy` (`ROUND_ROBIN|RANDOM|DISABLED`), `degraded[]`.

Proxy: `id`, masked `url`, `provider`, `dead_count`, `is_dead`, `last_failed_at`, `disabled`, `degraded[]`.

### QA nên check

- `POLICY_INVALID_LIMIT`, `POLICY_DOMAIN_INVALID`, `POLICY_STRATEGY_INVALID`.
- `POLICY_RATE_TOO_HIGH`: rps/concurrency vượt safe limit của QA/crawler policy.
- `POLICY_SOURCE_MISMATCH`: source config và effective domain policy khác nhưng không có override explanation.
- `PROXY_DEAD`, `PROXY_ALL_UNAVAILABLE`, `PROXY_DISABLED_SELECTED`.
- `PROXY_FAILURE_SPIKE`, `PROXY_RECOVERY_UNEXPLAINED`.
- `PROXY_SECRET_LEAK`: proxy credential xuất hiện trong response/log/UI/export; chỉ nhận URL masked khi đọc.

## 10. System values, settings và admin

### UI routes

`/policies`, `/settings/profile`, `/settings/api-keys`, `/settings/api-keys-guide`, `/admin`, `/admin/users`, `/admin/api-keys`, `/admin/audit-logs`, `/admin/system`.

### Functions quan sát được

- Profile: `fetchUserProfile`, update profile, update password.
- API keys: list/create/revoke; secret chỉ hiện một lần theo UI warning.
- Admin users: list/search, create, edit, delete, reset password, permissions (`crawl_manage`, `api_access`, `admin`, `all`), get user token/full permission.
- Audit logs: list/filter by time/user/method/path/search; detail request body/user agent/IP/status/duration.
- System: list/update/reload system values, gồm Boolean/Integer/String/Block Detection Rules/Prettify LLM.

### QA nên check (chỉ bật khi được cấp quyền admin rõ ràng)

- `ACCESS_CONTROL_REGRESSION`: read-only user đọc được endpoint mutation/admin.
- `PERMISSION_UI_MISMATCH`: UI ẩn control nhưng API không enforce, hoặc ngược lại.
- `API_KEY_SCOPE_TOO_BROAD`, `API_KEY_REVOKE_INEFFECTIVE`, `API_KEY_SECRET_REDISPLAYED`.
- `AUDIT_LOG_MISSING`, `AUDIT_LOG_PII_EXPOSURE`, `AUDIT_LOG_STATUS_MISMATCH`.
- `SYSTEM_VALUE_TYPE_MISMATCH`, `SYSTEM_VALUE_DEFAULT_DRIFT`.
- `LLM_CONFIG_INCOMPLETE`: enabled nhưng thiếu base_url/model/key/batch/concurrency/timeout.
- `BLOCK_RULE_INVALID_REGEX`, `BLOCK_RULE_UNREACHABLE`.

## 11. Đề xuất phạm vi triển khai

### P0 — duyệt để triển khai trước

Giữ đúng 15 rule MVP đã thống nhất: HTTP 404/429/5xx, auth redirect/login page, empty/very low, soft 404, CAPTCHA/anti-bot, mojibake/replacement char, clean empty/aggressive, exact duplicate. Bổ sung `UPSTREAM_SCHEMA_CHANGED`, `AUTH_FAILED`, và mapper theo schema thật của API.

### P1 — nên triển khai ngay sau khi có sample protected

`SOURCE_CONFIG_INVALID`, `JOB_COUNTER_INCONSISTENT`, `PAGE_JOB_SOURCE_MISMATCH`, `CONTENT_ROUTE_MISMATCH`, `PAGE_VIEW_EMPTY/TRUNCATED`, `FINAL_URL_DOMAIN_ESCAPE`, `CLEAN_PREVIEW_EXPORT_MISMATCH`, `EXPORT_FILTER_LEAK/ROW_COUNT_MISMATCH`, `PAGINATION_DUPLICATE_PAGE`, `PROXY_ALL_UNAVAILABLE`.

### P2 — phase sau / cần quyền và dữ liệu baseline

Near duplicate, source profile/IQR, boilerplate/link density, redirect chain, JS-render detection, regression giữa job, export archive integrity, permission/admin/audit/LLM rules.

## 12. Điều cần cung cấp để kiểm tra protected data

Các endpoint dữ liệu (`sources`, `jobs`, `pages`, `view`, `download`, `exports`) hiện trả `401 Authentication required`. Để chạy sample integration, cần một trong hai:

```env
CRAWLER_EMAIL=...
CRAWLER_PASSWORD=...
```

hoặc read-only API key/token. Không gửi password trong chat nếu không cần; đặt vào `.env` cục bộ hoặc secret manager rồi báo mình đã cấu hình. QA tool không gọi các endpoint mutation/delete.
