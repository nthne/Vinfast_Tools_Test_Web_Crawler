# Crawl History Audit

> Phân tích read-only các job crawl từ `2026-09-16` đến `2026-09-17`.

## Kết luận tổng quát

Đã kiểm tra **8 job**. Report phân biệt lỗi renderer/crawler, lỗi upstream/access, lỗi extraction và lỗi URL expansion; không coi mọi `FAILED` là lỗi website.

## Nhóm nguyên nhân

| Nhóm | Số record lỗi | Số job | Lý do | Hướng xử lý |
|---|---:|---:|---|---|
| **Renderer/CDP** | 775 | 5 | Browser renderer hoặc phiên CDP của crawler không sẵn sàng; lỗi xảy ra trước khi có HTTP response đáng tin cậy. | Kiểm tra health/worker capacity của renderer; thử HTTP-only nếu trang không cần JavaScript. |
| **Extraction/HTML structure** | 38 | 4 | Crawler nhận được shell HTML, body thiếu hoặc nội dung quá ít để extraction tạo page hợp lệ. | So sánh raw HTML với rendered DOM và kiểm tra selector/content extraction rule. |
| **proxy/403** | 33 | 1 | Crawler không có proxy phù hợp hoặc upstream trả 403 cho đường đi hiện tại. | Kiểm tra proxy pool, host policy và quyền truy cập; không coi đây là lỗi extraction. |
| **Retry exhausted** | 23 | 2 | Crawler đã thử lại nhưng số lần retry vẫn hết trước khi renderer/download hoàn tất. | Kiểm tra retry policy, giới hạn concurrency và lỗi gốc trước khi tăng retry vô hạn. |
| **SSRF/DNS security** | 15 | 4 | Crawler chặn download vì host không nằm trong allowlist hoặc DNS/peer không khớp kiểm tra an toàn. | Xác minh host hợp lệ rồi cập nhật allowlist/SSRF policy theo cách an toàn. |
| **Anti-bot/403** | 14 | 3 | Trang đích hoặc CDN trả trang chặn bot/403 thay vì nội dung tài liệu. | Kiểm tra authenticated/browser crawl và anti-bot policy; không bypass CAPTCHA tự động. |
| **Upstream/request 400** | 10 | 3 | Target hoặc request tạo ra URL/params mà upstream không chấp nhận. | Kiểm tra URL normalization, query parameters và redirect chain. |
| **Download HTTP 451** | 4 | 2 | Upstream từ chối cung cấp resource vì hạn chế pháp lý, khu vực hoặc chính sách truy cập. | Kiểm tra quyền truy cập và geography của endpoint; không retry vô hạn. |
| **Download HTTP 404** | 1 | 1 | Resource URL được crawler yêu cầu không tồn tại tại thời điểm kiểm tra. | Kiểm tra URL extraction/canonicalization và phân biệt resource 404 với page 404. |

## Chi tiết từng job

| Job | Source | Bắt đầu | Trạng thái | Page records | Failed records | Kết luận |
|---|---|---|---|---:|---:|---|
| `d61f29db-0079-46dd-82c5-23a159f8ea17` | `c306f333-5aaa-4325-abea-9ab2c276bdec` | `2026-09-16T07:33:07.581460Z` | `CANCELLED` | 17574 | 91 | proxy/403 (33), Extraction/HTML structure (25), Renderer/CDP (13) |

### Job `d61f29db-0079-46dd-82c5-23a159f8ea17`

- **Lý do (proxy/403, 33 record):** Crawler không có proxy phù hợp hoặc upstream trả 403 cho đường đi hiện tại.
  - **Nên kiểm tra:** Kiểm tra proxy pool, host policy và quyền truy cập; không coi đây là lỗi extraction.
- **Lý do (Extraction/HTML structure, 25 record):** Crawler nhận được shell HTML, body thiếu hoặc nội dung quá ít để extraction tạo page hợp lệ.
  - **Nên kiểm tra:** So sánh raw HTML với rendered DOM và kiểm tra selector/content extraction rule.
- **Lý do (Renderer/CDP, 13 record):** Browser renderer hoặc phiên CDP của crawler không sẵn sàng; lỗi xảy ra trước khi có HTTP response đáng tin cậy.
  - **Nên kiểm tra:** Kiểm tra health/worker capacity của renderer; thử HTTP-only nếu trang không cần JavaScript.
- **Lý do (Anti-bot/403, 9 record):** Trang đích hoặc CDN trả trang chặn bot/403 thay vì nội dung tài liệu.
  - **Nên kiểm tra:** Kiểm tra authenticated/browser crawl và anti-bot policy; không bypass CAPTCHA tự động.
- **Lý do (Upstream/request 400, 5 record):** Target hoặc request tạo ra URL/params mà upstream không chấp nhận.
  - **Nên kiểm tra:** Kiểm tra URL normalization, query parameters và redirect chain.
- **Lý do (SSRF/DNS security, 4 record):** Crawler chặn download vì host không nằm trong allowlist hoặc DNS/peer không khớp kiểm tra an toàn.
  - **Nên kiểm tra:** Xác minh host hợp lệ rồi cập nhật allowlist/SSRF policy theo cách an toàn.
- **Lý do (Download HTTP 451, 2 record):** Upstream từ chối cung cấp resource vì hạn chế pháp lý, khu vực hoặc chính sách truy cập.
  - **Nên kiểm tra:** Kiểm tra quyền truy cập và geography của endpoint; không retry vô hạn.
- **Lý do URL/budget:** phát hiện 1 URL có dấu hiệu path expansion, 3190 nhóm URL trùng và 3163 nhóm route biến thể trong page sample/toàn job.
  - **Nên kiểm tra:** URL canonicalization, pagination/calendar trap và việc resource URL có bị đưa vào navigation queue hay không.
- **Resource mix:** 7627 resource record; 297 có MIME image (3.9%). Resource ảnh thường là asset hợp lệ, nhưng không nên bị tính như navigation page hoặc làm cạn resource budget ngoài dự kiến.
- **Lý do số liệu:** job metadata báo total=17574, failed=85 nhưng page endpoint trả total=17574, failed=91; cần kiểm tra consistency giữa hai API.
- **Trạng thái:** Job bị CANCELLED; các lỗi còn lại không thể dùng để đánh giá toàn bộ source như một crawl hoàn tất.

**Error signatures:**

| Code | Message | Count |
|---|---|---:|
| `NO_PROXY_AVAILABLE` | HTTP_403 | 33 |
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP discovery failed: error sending request | 11 |
| `CRW_PERMANENT` | Blocked by anti-bot (generic_block): Access Denied on short page (HTTP 403, 111 bytes) | 7 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (2897 bytes, 46 chars visible)) | 6 |
| `CRW_PERMANENT` | Target returned 400 Bad Request | 5 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (175 bytes, 0 chars visible)) | 2 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (209 bytes, 0 chars visible)) | 2 |
| `DOWNLOAD_HTTP_451` | Download failed with HTTP 451 | 2 |
| `UNSAFEDOWNLOADURL` | Connected peer differs from the validated DNS result | 2 |
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed | 2 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: no_content_elements, script_heavy_shell (34978 bytes, 63 chars visible)) | 2 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (48023 bytes, 0 chars visible)) | 2 |
| `CRW_PERMANENT` | Blocked by anti-bot (generic_block): HTTP 403 with HTML content (478 bytes) | 2 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (174 bytes, 0 chars visible)) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (7877 bytes, 0 chars visible)) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (176 bytes, 0 chars visible)) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (294 bytes, 0 chars visible)) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (198 bytes, 0 chars visible)) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (686 bytes, 46 chars visible)) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (9191 bytes, 0 chars visible)) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (183 bytes, 0 chars visible)) | 1 |
| `UNSAFE_TARGET_URL` | Download host could not be resolved (add the host to ssrf_allowed_hosts if this is intended) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (241 bytes, 0 chars visible)) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (180 bytes, 0 chars visible)) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (11537 bytes, 0 chars visible)) | 1 |
| `UNSAFEDOWNLOADURL` | Download host could not be resolved | 1 |

| `c875447b-f918-444f-ad59-09d43cfe4f49` | `76c5c3c9-faa5-4dd8-bd64-2794d78723fe` | `2026-09-16T07:38:01.094829Z` | `CANCELLED` | 211 | 1 | Extraction/HTML structure (1) |

### Job `c875447b-f918-444f-ad59-09d43cfe4f49`

- **Lý do (Extraction/HTML structure, 1 record):** Crawler nhận được shell HTML, body thiếu hoặc nội dung quá ít để extraction tạo page hợp lệ.
  - **Nên kiểm tra:** So sánh raw HTML với rendered DOM và kiểm tra selector/content extraction rule.
- **Lý do URL/budget:** phát hiện 0 URL có dấu hiệu path expansion, 27 nhóm URL trùng và 28 nhóm route biến thể trong page sample/toàn job.
  - **Nên kiểm tra:** URL canonicalization, pagination/calendar trap và việc resource URL có bị đưa vào navigation queue hay không.
- **Resource mix:** 90 resource record; 39 có MIME image (43.3%). Resource ảnh thường là asset hợp lệ, nhưng không nên bị tính như navigation page hoặc làm cạn resource budget ngoài dự kiến.
- **Lý do số liệu:** job metadata báo total=211, failed=2 nhưng page endpoint trả total=211, failed=1; cần kiểm tra consistency giữa hai API.
- **Trạng thái:** Job bị CANCELLED; các lỗi còn lại không thể dùng để đánh giá toàn bộ source như một crawl hoàn tất.

**Error signatures:**

| Code | Message | Count |
|---|---|---:|
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (11537 bytes, 0 chars visible)) | 1 |

| `49ddbae0-3320-4d15-9ffa-eeaf69099d68` | `c306f333-5aaa-4325-abea-9ab2c276bdec` | `2026-09-16T07:41:09.097709Z` | `COMPLETED` | 21200 | 603 | Renderer/CDP (573), Retry exhausted (9), SSRF/DNS security (8) |

### Job `49ddbae0-3320-4d15-9ffa-eeaf69099d68`

- **Lý do (Renderer/CDP, 573 record):** Browser renderer hoặc phiên CDP của crawler không sẵn sàng; lỗi xảy ra trước khi có HTTP response đáng tin cậy.
  - **Nên kiểm tra:** Kiểm tra health/worker capacity của renderer; thử HTTP-only nếu trang không cần JavaScript.
- **Lý do (Retry exhausted, 9 record):** Crawler đã thử lại nhưng số lần retry vẫn hết trước khi renderer/download hoàn tất.
  - **Nên kiểm tra:** Kiểm tra retry policy, giới hạn concurrency và lỗi gốc trước khi tăng retry vô hạn.
- **Lý do (SSRF/DNS security, 8 record):** Crawler chặn download vì host không nằm trong allowlist hoặc DNS/peer không khớp kiểm tra an toàn.
  - **Nên kiểm tra:** Xác minh host hợp lệ rồi cập nhật allowlist/SSRF policy theo cách an toàn.
- **Lý do (Extraction/HTML structure, 8 record):** Crawler nhận được shell HTML, body thiếu hoặc nội dung quá ít để extraction tạo page hợp lệ.
  - **Nên kiểm tra:** So sánh raw HTML với rendered DOM và kiểm tra selector/content extraction rule.
- **Lý do (Anti-bot/403, 3 record):** Trang đích hoặc CDN trả trang chặn bot/403 thay vì nội dung tài liệu.
  - **Nên kiểm tra:** Kiểm tra authenticated/browser crawl và anti-bot policy; không bypass CAPTCHA tự động.
- **Lý do (Upstream/request 400, 2 record):** Target hoặc request tạo ra URL/params mà upstream không chấp nhận.
  - **Nên kiểm tra:** Kiểm tra URL normalization, query parameters và redirect chain.
- **Lý do URL/budget:** phát hiện 15694 URL có dấu hiệu path expansion, 1206 nhóm URL trùng và 1209 nhóm route biến thể trong page sample/toàn job.
  - **Nên kiểm tra:** URL canonicalization, pagination/calendar trap và việc resource URL có bị đưa vào navigation queue hay không.
- **Resource mix:** 20010 resource record; 3673 có MIME image (18.4%). Resource ảnh thường là asset hợp lệ, nhưng không nên bị tính như navigation page hoặc làm cạn resource budget ngoài dự kiến.
- **Lý do số liệu:** job metadata báo total=21200, failed=602 nhưng page endpoint trả total=21200, failed=603; cần kiểm tra consistency giữa hai API.

**Error signatures:**

| Code | Message | Count |
|---|---|---:|
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed | 220 |
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: No JS renderer available | 188 |
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP discovery failed: error sending request | 165 |
| `UNSAFE_TARGET_URL` | Download host could not be resolved (add the host to ssrf_allowed_hosts if this is intended) | 6 |
| `CRWTEMPORARYERROR` | crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP discovery failed: error sending request | 4 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: no_content_elements, script_heavy_shell (34978 bytes, 63 chars visible)) | 3 |
| `CRWTEMPORARYERROR` | crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: No JS renderer available | 3 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (294 bytes, 0 chars visible)) | 3 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (2897 bytes, 46 chars visible)) | 2 |
| `CRWTEMPORARYERROR` | crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP Target.createTarget: WS closed | 2 |
| `CRW_PERMANENT` | Target returned 400 Bad Request | 2 |
| `CRW_PERMANENT` | Blocked by anti-bot (generic_block): HTTP 403 with HTML content (478 bytes) | 2 |
| `UNSAFEDOWNLOADURL` | Download host could not be resolved | 1 |
| `UNSAFEDOWNLOADURL` | Connected peer differs from the validated DNS result | 1 |
| `CRW_PERMANENT` | Blocked by anti-bot (generic_block): HTTP 403 with near-empty response (21 bytes) | 1 |

| `7958f96e-37d1-463d-b6e3-6374b988fe7a` | `76c5c3c9-faa5-4dd8-bd64-2794d78723fe` | `2026-09-16T07:42:55.470467Z` | `COMPLETED` | 42 | 1 | SSRF/DNS security (1) |

### Job `7958f96e-37d1-463d-b6e3-6374b988fe7a`

- **Lý do (SSRF/DNS security, 1 record):** Crawler chặn download vì host không nằm trong allowlist hoặc DNS/peer không khớp kiểm tra an toàn.
  - **Nên kiểm tra:** Xác minh host hợp lệ rồi cập nhật allowlist/SSRF policy theo cách an toàn.
- **Resource mix:** 41 resource record; 40 có MIME image (97.6%). Resource ảnh thường là asset hợp lệ, nhưng không nên bị tính như navigation page hoặc làm cạn resource budget ngoài dự kiến.

**Error signatures:**

| Code | Message | Count |
|---|---|---:|
| `UNSAFE_TARGET_URL` | Download host could not be resolved (add the host to ssrf_allowed_hosts if this is intended) | 1 |

| `656ec477-a92f-41ef-bda5-ee9374eaa156` | `30d6118e-da6e-49cc-baa6-b4b29abeaaa8` | `2026-09-16T10:18:19.823928Z` | `COMPLETED` | 108 | 80 | Renderer/CDP (80) |

### Job `656ec477-a92f-41ef-bda5-ee9374eaa156`

- **Lý do (Renderer/CDP, 80 record):** Browser renderer hoặc phiên CDP của crawler không sẵn sàng; lỗi xảy ra trước khi có HTTP response đáng tin cậy.
  - **Nên kiểm tra:** Kiểm tra health/worker capacity của renderer; thử HTTP-only nếu trang không cần JavaScript.
- **Resource mix:** 8 resource record; 6 có MIME image (75.0%). Resource ảnh thường là asset hợp lệ, nhưng không nên bị tính như navigation page hoặc làm cạn resource budget ngoài dự kiến.

**Error signatures:**

| Code | Message | Count |
|---|---|---:|
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed | 43 |
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP discovery failed: error sending request | 37 |

| `682cc920-4323-4469-87f5-ef2200c89097` | `76c5c3c9-faa5-4dd8-bd64-2794d78723fe` | `2026-09-17T08:12:20.889338Z` | `COMPLETED` | 21 | 0 | NO_FAILURES |

### Job `682cc920-4323-4469-87f5-ef2200c89097`

**Kết luận:** Không có page failed trong dữ liệu page endpoint của job này.
- **Resource mix:** 20 resource record; 20 có MIME image (100.0%). Resource ảnh thường là asset hợp lệ, nhưng không nên bị tính như navigation page hoặc làm cạn resource budget ngoài dự kiến.

**Error signatures:**

| Code | Message | Count |
|---|---|---:|
| - | Không có error signature | 0 |

| `c5a658df-6d8d-45ef-bfc8-3ccb9e8b1773` | `30d6118e-da6e-49cc-baa6-b4b29abeaaa8` | `2026-09-17T10:32:16.841867Z` | `COMPLETED` | 108 | 80 | Renderer/CDP (80) |

### Job `c5a658df-6d8d-45ef-bfc8-3ccb9e8b1773`

- **Lý do (Renderer/CDP, 80 record):** Browser renderer hoặc phiên CDP của crawler không sẵn sàng; lỗi xảy ra trước khi có HTTP response đáng tin cậy.
  - **Nên kiểm tra:** Kiểm tra health/worker capacity của renderer; thử HTTP-only nếu trang không cần JavaScript.
- **Resource mix:** 8 resource record; 6 có MIME image (75.0%). Resource ảnh thường là asset hợp lệ, nhưng không nên bị tính như navigation page hoặc làm cạn resource budget ngoài dự kiến.

**Error signatures:**

| Code | Message | Count |
|---|---|---:|
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed | 48 |
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP discovery failed: error sending request | 32 |

| `e8e5c6ad-27f8-4585-83d2-ac9423d1cc47` | `c306f333-5aaa-4325-abea-9ab2c276bdec` | `2026-09-17T11:29:21.054873Z` | `COMPLETED` | 3200 | 57 | Renderer/CDP (29), Retry exhausted (14), Extraction/HTML structure (4) |

### Job `e8e5c6ad-27f8-4585-83d2-ac9423d1cc47`

- **Lý do (Renderer/CDP, 29 record):** Browser renderer hoặc phiên CDP của crawler không sẵn sàng; lỗi xảy ra trước khi có HTTP response đáng tin cậy.
  - **Nên kiểm tra:** Kiểm tra health/worker capacity của renderer; thử HTTP-only nếu trang không cần JavaScript.
- **Lý do (Retry exhausted, 14 record):** Crawler đã thử lại nhưng số lần retry vẫn hết trước khi renderer/download hoàn tất.
  - **Nên kiểm tra:** Kiểm tra retry policy, giới hạn concurrency và lỗi gốc trước khi tăng retry vô hạn.
- **Lý do (Extraction/HTML structure, 4 record):** Crawler nhận được shell HTML, body thiếu hoặc nội dung quá ít để extraction tạo page hợp lệ.
  - **Nên kiểm tra:** So sánh raw HTML với rendered DOM và kiểm tra selector/content extraction rule.
- **Lý do (Upstream/request 400, 3 record):** Target hoặc request tạo ra URL/params mà upstream không chấp nhận.
  - **Nên kiểm tra:** Kiểm tra URL normalization, query parameters và redirect chain.
- **Lý do (SSRF/DNS security, 2 record):** Crawler chặn download vì host không nằm trong allowlist hoặc DNS/peer không khớp kiểm tra an toàn.
  - **Nên kiểm tra:** Xác minh host hợp lệ rồi cập nhật allowlist/SSRF policy theo cách an toàn.
- **Lý do (Download HTTP 451, 2 record):** Upstream từ chối cung cấp resource vì hạn chế pháp lý, khu vực hoặc chính sách truy cập.
  - **Nên kiểm tra:** Kiểm tra quyền truy cập và geography của endpoint; không retry vô hạn.
- **Lý do (Anti-bot/403, 2 record):** Trang đích hoặc CDN trả trang chặn bot/403 thay vì nội dung tài liệu.
  - **Nên kiểm tra:** Kiểm tra authenticated/browser crawl và anti-bot policy; không bypass CAPTCHA tự động.
- **Lý do (Download HTTP 404, 1 record):** Resource URL được crawler yêu cầu không tồn tại tại thời điểm kiểm tra.
  - **Nên kiểm tra:** Kiểm tra URL extraction/canonicalization và phân biệt resource 404 với page 404.
- **Lý do URL/budget:** phát hiện 0 URL có dấu hiệu path expansion, 135 nhóm URL trùng và 168 nhóm route biến thể trong page sample/toàn job.
  - **Nên kiểm tra:** URL canonicalization, pagination/calendar trap và việc resource URL có bị đưa vào navigation queue hay không.
- **Resource mix:** 2000 resource record; 1866 có MIME image (93.3%). Resource ảnh thường là asset hợp lệ, nhưng không nên bị tính như navigation page hoặc làm cạn resource budget ngoài dự kiến.
- **Lý do số liệu:** job metadata báo total=3200, failed=56 nhưng page endpoint trả total=3200, failed=57; cần kiểm tra consistency giữa hai API.

**Error signatures:**

| Code | Message | Count |
|---|---|---:|
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP Target.createTarget: WS closed | 17 |
| `CRW_PERMANENT` | js_escalation_failed: Renderer error: CDP discovery failed: error sending request | 12 |
| `CRWTEMPORARYERROR` | crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP discovery failed: error sending request | 6 |
| `CRWTEMPORARYERROR` | crw temporary failure retries exhausted: crw returned HTTP 500: Renderer error: CDP Target.createTarget: WS closed | 4 |
| `CRWTEMPORARYERROR` | crw temporary failure retries exhausted:  | 4 |
| `CRW_PERMANENT` | Target returned 400 Bad Request | 3 |
| `DOWNLOAD_HTTP_451` | Download failed with HTTP 451 | 2 |
| `UNSAFEDOWNLOADURL` | Connected peer differs from the validated DNS result | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (686 bytes, 46 chars visible)) | 1 |
| `CRW_PERMANENT` | Blocked by anti-bot (generic_block): HTTP 403 with near-empty response (21 bytes) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: no <body> tag (1377 bytes)) | 1 |
| `UNSAFE_TARGET_URL` | Download host could not be resolved (add the host to ssrf_allowed_hosts if this is intended) | 1 |
| `DOWNLOAD_HTTP_404` | Download failed with HTTP 404 | 1 |
| `CRW_PERMANENT` | Blocked by anti-bot (generic_block): HTTP 403 with HTML content (478 bytes) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (294 bytes, 0 chars visible)) | 1 |
| `CRW_PERMANENT` | No usable content could be extracted (Structural: minimal_text, no_content_elements, script_heavy_shell (11537 bytes, 0 chars visible)) | 1 |

## Ghi chú đọc số liệu

- `page records` và `failed records` được tính từ page endpoint; job metadata có thể lệch và được ghi riêng trong chi tiết job.
- Lỗi không có HTTP status thường xảy ra trước response, nên không được kết luận là website trả 4xx/5xx.
- Job CANCELLED được giữ lại để giải thích nguyên nhân dừng, nhưng không được coi là crawl hoàn tất.
- Report không retry, cancel, update hoặc delete dữ liệu crawler.
