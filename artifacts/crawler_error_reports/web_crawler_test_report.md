# Báo cáo kiểm thử Web Crawler

**Ngày lập:** 18/09/2026  
**Phạm vi:** các job Foody và PyTorch được ghi nhận ngày 16–17/09/2026 UTC  
**Phương thức:** đọc dữ liệu crawler/API ở chế độ read-only; không retry, cancel, delete hoặc thay đổi job.

## 1. Giới thiệu tool

Đây là bộ tool kiểm thử chất lượng dữ liệu web crawler, không phải crawler chính. Tool truy cập source/job/page đã crawl, chuẩn hóa dữ liệu, phát hiện lỗi theo rule, lưu bằng chứng và xuất báo cáo để đội phát triển crawler có thể kiểm tra nguyên nhân.

Các chức năng chính:

- kiểm tra source, job, page và các record failed;
- phân biệt lỗi renderer, extraction, scope, URL, resource/page và upstream;
- phát hiện URL ngoài scope, duplicate, route expansion, MIME/classification mismatch và lỗi cấu hình dễ gây over-crawl;
- sinh summary ngắn gọn và report chi tiết theo từng nhóm lỗi;
- hoạt động read-only, credentials chỉ đọc từ biến môi trường.

Mã nguồn, tool và báo cáo chi tiết: [GitHub repository](https://github.com/nthne/Vinfast_Tools_Test_Web_Crawler).

## 2. Kết luận tổng quan

**Kết quả kiểm thử: FAIL – chưa nên tin cậy kết quả crawl toàn source trước khi xử lý các lỗi pipeline ưu tiên cao.**

Các vấn đề chính:

1. Renderer/CDP thất bại lặp lại trên PyTorch: 80/108 page failed ở cả hai job.
2. Job Foody lưu nhiều URL ngoài phạm vi source; resource HTML và asset bị xử lý như navigation/page.
3. Canonicalization/deduplication chưa đủ chặt, xuất hiện repeated path, duplicate và route variant.
4. Tham số Page budget/Resource budget khó hiểu, mặc định quá lớn và có nguy cơ làm người dùng mới crawl nhiều dữ liệu thừa mà không biết rõ chi phí.
5. PyTorch có dấu hiệu resolve relative URL sai do source URL thiếu dấu `/` cuối.

## 3. Số liệu kiểm thử

| Chỉ số | Kết quả |
|---|---:|
| Job được kiểm tra | 8 |
| Source liên quan | 3 |
| Page record quan sát | 42.464 |
| Failed record quan sát | 913 |
| Thời gian | 16–17/09/2026 UTC |

| Nhóm lỗi | Số record | Đánh giá |
|---|---:|---|
| Renderer/CDP | 775 | Critical – lỗi hạ tầng crawler |
| Extraction/HTML | 38 | High – cần phân biệt shell, render và extractor |
| Proxy/403 | 33 | High – crawler/proxy hoặc upstream policy |
| Retry exhausted | 23 | High – retry chưa xử lý đúng error class |
| SSRF/DNS security | 15 | Medium/High – cần diagnostic rõ hơn |
| Anti-bot/403 | 14 | Medium – upstream chặn hoặc policy truy cập |
| Request 400 | 10 | Medium – URL/query/redirect |
| HTTP 451 | 4 | Medium – upstream từ chối resource |
| HTTP 404 | 1 | Medium – resource không tồn tại |

## 4. Ma trận job

| Job | Source | Ngày | Trạng thái | Records | Failed | Nhận định ngắn |
|---|---|---|---|---:|---:|---|
| `d61f29db-0079-46dd-82c5-23a159f8ea17` | Foody main | 16/9 | CANCELLED | 17.574 | 91 | Queue lớn, proxy/403, extraction, renderer, URL expansion |
| `c875447b-f918-444f-ad59-09d43cfe4f49` | Foody single URL | 16/9 | CANCELLED | 211 | 1 | Extraction, duplicate/route variant |
| `49ddbae0-3320-4d15-9ffa-eeaf69099d68` | Foody main | 16/9 | COMPLETED | 21.200 | 603 | Đạt runtime effective budget; có scope leak và renderer failure |
| `7958f96e-37d1-463d-b6e3-6374b988fe7a` | Foody single URL | 16/9 | COMPLETED | 42 | 1 | SSRF/DNS safety guard |
| `656ec477-a92f-41ef-bda5-ee9374eaa156` | PyTorch | 16/9 | COMPLETED | 108 | 80 | Renderer/CDP failure diện rộng |
| `682cc920-4323-4469-87f5-ef2200c89097` | Foody single URL | 17/9 | COMPLETED | 21 | 0 | Không có failed page |
| `c5a658df-6d8d-45ef-bfc8-3ccb9e8b1773` | PyTorch | 17/9 | COMPLETED | 108 | 80 | Renderer/CDP failure diện rộng |
| `e8e5c6ad-27f8-4585-83d2-ac9423d1cc47` | Foody main | 17/9 | COMPLETED | 3.200 | 57 | Renderer, retry, extraction, anti-bot, HTTP/resource |

## 5. Danh sách lỗi cần ưu tiên

| Mức | Lỗi | Kết luận kiểm thử | Chi tiết |
|---|---|---|---|
| Critical | Renderer/CDP failure | PyTorch failed 80/108 page ở cả hai job; lỗi xảy ra trước khi có HTTP status đáng tin cậy. | [CDP reports](errors/crw_permanent_3b1a353a482c.md), [CDP discovery](errors/crw_permanent_2ba5aa22751c.md), [No renderer](errors/crw_permanent_b1e9c9438157.md) |
| Critical | URL scope leak | Foody lưu nhiều URL Microsoft, Google, X/Twitter ngoài `foody.vn`; resource HTML còn bị parse link. | [Out-of-scope URL leak](errors/out_of_scope_url_leak_9a0fc4ee81e1.md) |
| High | URL expansion và deduplication | Có repeated path, duplicate và route variant; cần canonicalize trước enqueue/persistence và tách navigation/resource queue. | [Crawl history audit](crawl_history_audit_2026-09-16_2026-09-17.md) |
| High | Resource/page classification | `.png`, `.svg`, `.ico` có lúc bị ghi như page/navigation; một số resource trả HTML nhưng không nên mở rộng queue navigation. | [Crawl history audit](crawl_history_audit_2026-09-16_2026-09-17.md) |
| High | Relative URL resolution | Source PyTorch thiếu `/` cuối làm link tương đối có thể resolve thành `/docs/utils.html` thay vì `/docs/main/utils.html` hoặc `/docs/2.14/utils.html`. | [Source URL report](errors/source_url_missing_trailing_slash_158e3208f479.md) |
| High | Cấu hình budget khó hiểu | “Page budget” và “Resource budget” chưa rõ nghĩa; mặc định quá lớn có thể khiến người dùng mới tốn nhiều thời gian và tải dữ liệu thừa khi chất lượng chưa được đảm bảo. | Đề xuất cải thiện UX/config, không phải lỗi runtime tự tăng budget. |
| Medium/High | Proxy, anti-bot và HTTP 403 | Cần tách rõ lỗi proxy pool, upstream anti-bot và permission để retry/action đúng. | [No proxy](errors/no_proxy_available_2e5558325302.md), [Anti-bot](errors/crw_permanent_e699dcbc184f.md) |
| Medium/High | SSRF/DNS validation | Cơ chế chặn có tác dụng nhưng thông báo allowlist/DNS chưa đủ rõ để debug. | [Unsafe target](errors/unsafe_target_url_b1ec305ad5b4.md), [Unsafe download](errors/unsafedownloadurl_a370df1de898.md) |
| High | Extraction/HTML shell | Có record shell HTML, empty body, minimal text và no content elements; cần lưu raw/rendered evidence. | [Crawler error summary](crawler_error_summary.md) |
| Medium | Counter consistency | Job metadata và page endpoint có lúc trả failed count khác nhau; cần thống nhất snapshot/version. | [Crawl history audit](crawl_history_audit_2026-09-16_2026-09-17.md) |

## 6. Kiểm thử chức năng

| ID | Chức năng | Kết quả | Ghi chú |
|---|---|---|---|
| TC-01 | Crawl trong source domain | PARTIAL | Có record hợp lệ nhưng job Foody lớn bị mở rộng ngoài scope |
| TC-02 | Enforce navigation allowlist | FAIL | Xuất hiện Microsoft, Google, X/Twitter trong Foody |
| TC-03 | Phân biệt page/resource | FAIL | Có MIME/kind mismatch và resource HTML bị dùng để mở rộng link |
| TC-04 | Hiểu và cấu hình page/resource budget | NEEDS IMPROVEMENT | Tên, ý nghĩa và default chưa đủ rõ; không kết luận runtime tự đổi budget |
| TC-05 | Canonicalize/dedupe URL | FAIL | Có repeated path, duplicate và route variant |
| TC-06 | Dừng crawl/quan sát budget | INCONCLUSIVE | Job `49dd...` đạt đúng runtime effective budget; cần metric queue/processed rõ hơn để đánh giá job còn lại |
| TC-07 | Browser renderer/CDP | FAIL | PyTorch 160/216 page failed do renderer/CDP |
| TC-08 | HTML extraction | FAIL | Có shell HTML, empty body và minimal content |
| TC-09 | Retry policy | FAIL | Có retry exhausted nhưng thiếu phân loại nguyên nhân nhất quán |
| TC-10 | Proxy/anti-bot | FAIL/PARTIAL | Có `NO_PROXY_AVAILABLE`, 403 và anti-bot response |
| TC-11 | SSRF/DNS protection | PASS về mặt chặn, PARTIAL về usability | Có chặn nhưng cần evidence/policy rõ hơn |
| TC-12 | Relative URL resolution | FAIL | Source PyTorch thiếu slash cuối |
| TC-13 | Counter/report consistency | FAIL | Metadata và page endpoint có failed count khác nhau |
| TC-14 | Job nhỏ không lỗi | PASS | Foody single URL ngày 17 không có failed page |

## 7. Đề xuất xử lý

### P0

1. Sửa và kiểm thử renderer/CDP bằng sample 10–20 page.
2. Enforce navigation allowlist theo source.
3. Không follow link từ resource trả HTML như một navigation page.
4. Sửa canonicalization, repeated path và deduplication.
5. Tách rõ page/resource queue và hiển thị budget thực tế.

### P1

1. Đổi tên/giải thích rõ Page budget và Resource budget, hiển thị tổng chi phí dự kiến trước khi chạy.
2. Giảm default budget hoặc yêu cầu người dùng xác nhận khi giá trị lớn.
3. Chuẩn hóa source URL và resolve relative URL theo `final_url`.
4. Phân loại proxy 403, anti-bot 403 và permission 403.
5. Bổ sung raw HTML, rendered DOM, requested URL và final URL vào evidence.

### P2

1. Đồng bộ snapshot counter giữa job metadata và page endpoint.
2. Thêm regression metrics giữa các crawl job.
3. Hiển thị rõ `NAVIGATION`/`RESOURCE`, MIME, queue count và processed count.
4. Cảnh báo khi external-host ratio hoặc image-resource ratio tăng bất thường.

## 8. Tiêu chí kiểm thử lại

- PyTorch sample tối thiểu 20 URL không còn lỗi CDP diện rộng.
- Foody sample không tạo navigation ngoài allowlist.
- Resource `.png/.svg/.ico` không được dùng để mở rộng navigation chỉ vì response trả HTML.
- Repeated path và duplicate giảm dưới ngưỡng đã cấu hình.
- Page budget, resource budget, queue count và processed count được hiển thị thống nhất.
- Tên, mô tả và giá trị mặc định của budget đủ rõ để người dùng mới hiểu trước khi chạy.
- Metadata failed count và page endpoint failed count khớp trong cùng snapshot.
- Relative link của PyTorch resolve đúng theo `/docs/main/...` hoặc version path.

## 9. Báo cáo chi tiết và nguồn dữ liệu

Các bằng chứng, page record, runtime metadata và hướng xử lý chi tiết nằm trong repository:

- [Crawler error summary](crawler_error_summary.md)
- [Crawl history audit 16–17/9](crawl_history_audit_2026-09-16_2026-09-17.md)
- [Các report chi tiết theo lỗi](errors/)

**GitHub repository:** [nthne/Vinfast_Tools_Test_Web_Crawler](https://github.com/nthne/Vinfast_Tools_Test_Web_Crawler). 
Repository chứa project `test_web_crawler`, các tool, unit tests, tài liệu và report chi tiết.

## 10. Kết luận

Tool đã cung cấp bằng chứng để xác định các vấn đề chính nằm ở renderer/CDP, scope enforcement, phân loại page/resource, canonicalization và khả năng sử dụng cấu hình budget. Các lỗi upstream như anti-bot, 403, 404 hoặc 451 cần được tách riêng, không quy toàn bộ cho website nguồn.
