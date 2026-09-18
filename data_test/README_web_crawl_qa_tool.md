# Web Crawl QA Tool

## 1. Mục tiêu

Xây dựng một công cụ **kiểm tra chất lượng dữ liệu web crawl** dành cho các source đã được crawl và lưu trong một hệ thống web nội bộ. Hệ thống nguồn yêu cầu **đăng nhập bằng email/password** mới xem được danh sách source, job và các bản ghi đã crawl.

Email/password thực tế **sẽ được cung cấp sau**. Trong quá trình phát triển, tuyệt đối không hard-code tài khoản vào source code. Chỉ sử dụng biến môi trường hoặc secret manager.

Công cụ QA phải có khả năng:

- Đăng nhập vào hệ thống crawl hoặc sử dụng API/token nếu hệ thống hỗ trợ.
- Truy cập các source, job và page/content đã crawl.
- Thu thập metadata và nội dung cần thiết để kiểm tra lỗi.
- Phát hiện lỗi crawl, lỗi extraction, lỗi cleaning, duplicate, soft-404, CAPTCHA, lỗi encoding, bất thường dữ liệu và lỗi cấu trúc.
- Cho phép kiểm tra từng page hoặc toàn bộ source.
- Hiển thị thống kê tổng quan, danh sách lỗi và chi tiết từng page.
- Có khả năng export báo cáo QA ra CSV/JSON/Parquet.
- Có thiết kế đủ modular để mở rộng thêm rule mới sau này.

---

# 2. Phạm vi hệ thống

Tool QA **không phải crawler chính**. Nó không có nhiệm vụ crawl lại Internet từ đầu trừ khi cần một request kiểm tra đối chứng.

Luồng chính:

```text
Crawler Platform
    ↓
Authenticated access
    ↓
Sources / Jobs / Crawled pages
    ↓
QA Tool
    ↓
Validation / Detection / Statistics
    ↓
Dashboard + Error list + Export
```

Tool phải ưu tiên đọc dữ liệu đã crawl từ backend/API của hệ thống crawler.

Nếu hệ thống không có API public rõ ràng, có thể fallback sang:

1. authenticated HTTP session;
2. browser automation bằng Playwright;
3. đọc endpoint XHR/fetch mà giao diện web đang dùng.

Không nên scrape trực tiếp DOM của giao diện nếu có thể lấy JSON từ API nội bộ.

---

# 3. Nguyên tắc xác thực

## 3.1. Credentials

Thông tin đăng nhập sẽ được cung cấp sau dưới dạng:

```text
CRAWLER_EMAIL=...
CRAWLER_PASSWORD=...
```

Tạo file:

```text
.env.example
```

với nội dung:

```env
CRAWLER_BASE_URL=
CRAWLER_EMAIL=
CRAWLER_PASSWORD=
CRAWLER_API_KEY=
CRAWLER_AUTH_MODE=auto
```

Không commit `.env` lên Git.

Thêm vào `.gitignore`:

```gitignore
.env
.env.*
!.env.example
*.log
__pycache__/
.pytest_cache/
.venv/
node_modules/
exports/
artifacts/
```

## 3.2. Thứ tự ưu tiên auth

Agent phải thử theo thứ tự:

### Mode A — API Key / Bearer Token

Nếu hệ thống có API key hoặc token, ưu tiên cách này.

Header ví dụ:

```http
Authorization: Bearer <token>
```

### Mode B — Login API

Nếu frontend login thông qua endpoint như:

```http
POST /api/login
POST /auth/login
POST /api/auth/sign-in
```

thì dùng `requests.Session()` hoặc `httpx.Client()` để login và giữ cookie/session.

### Mode C — Browser session

Nếu login cần JavaScript, SSO, CSRF phức tạp hoặc cookie được tạo qua browser, dùng Playwright.

Sau khi login thành công:

- lưu storage state;
- reuse cho các lần chạy sau;
- nếu session hết hạn thì tự login lại.

Ví dụ:

```text
artifacts/auth/storage_state.json
```

Không log password.

---

# 4. Khảo sát hệ thống crawler trước khi code sâu

Agent cần làm bước discovery trước.

## 4.1. Xác định các endpoint chính

Tìm các endpoint tương ứng với:

```text
GET sources
GET source detail
GET jobs
GET job detail
GET pages/content
GET page detail
GET raw content
GET cleaned content
GET export
```

Nếu giao diện gọi XHR/fetch, ưu tiên dùng chính các API này.

## 4.2. Ghi lại schema thực tế

Tạo file:

```text
docs/crawler_api_observed.md
```

Ghi lại:

- endpoint;
- method;
- query params;
- pagination;
- auth header/cookie;
- sample response;
- field mapping.

Ví dụ mapping:

```text
source_id      -> id
source_name    -> name
page_id        -> page.id
url            -> page.url
status_code    -> response.status
raw_html       -> raw_html
raw_text       -> raw_text
clean_text     -> clean_text
markdown       -> markdown
created_at     -> crawled_at
```

Không giả định field name trước khi khảo sát.

---

# 5. Kiến trúc đề xuất

Khuyến nghị Python 3.11+.

Stack đề xuất:

- FastAPI — backend API/UI service.
- httpx — gọi API crawler.
- Playwright — auth/browser fallback.
- pandas / pyarrow — xử lý dataset và Parquet.
- BeautifulSoup / lxml — HTML analysis.
- rapidfuzz — similarity cơ bản.
- datasketch hoặc simhash — near duplicate.
- scikit-learn — anomaly detection ở phase sau.
- pydantic — schema/config.
- SQLite cho MVP, PostgreSQL nếu cần multi-user / scale.

Frontend có thể dùng:

- React/Vite;
- hoặc server-rendered FastAPI/Jinja cho MVP.

Ưu tiên chức năng hơn giao diện đẹp trong version đầu.

---

# 6. Cấu trúc project đề xuất

```text
web-crawl-qa/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── logging.py
│   │
│   ├── auth/
│   │   ├── base.py
│   │   ├── api_key.py
│   │   ├── session_auth.py
│   │   └── playwright_auth.py
│   │
│   ├── crawler_client/
│   │   ├── client.py
│   │   ├── schemas.py
│   │   ├── pagination.py
│   │   └── mapper.py
│   │
│   ├── qa/
│   │   ├── engine.py
│   │   ├── models.py
│   │   ├── registry.py
│   │   ├── context.py
│   │   └── rules/
│   │       ├── http_rules.py
│   │       ├── content_rules.py
│   │       ├── auth_rules.py
│   │       ├── cleaning_rules.py
│   │       ├── duplicate_rules.py
│   │       ├── encoding_rules.py
│   │       ├── structure_rules.py
│   │       └── anomaly_rules.py
│   │
│   ├── services/
│   │   ├── source_service.py
│   │   ├── page_service.py
│   │   ├── qa_service.py
│   │   ├── export_service.py
│   │   └── profile_service.py
│   │
│   ├── storage/
│   │   ├── db.py
│   │   ├── models.py
│   │   └── repository.py
│   │
│   └── api/
│       ├── sources.py
│       ├── pages.py
│       ├── qa.py
│       └── exports.py
│
├── frontend/
│   └── ...
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/
│   ├── crawler_api_observed.md
│   ├── error_codes.md
│   └── architecture.md
│
├── exports/
├── artifacts/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 7. Data model nội bộ

Mỗi page nên được normalize về schema chung.

```python
class CrawledPage:
    page_id: str
    source_id: str
    job_id: str | None
    url: str
    final_url: str | None
    title: str | None
    status_code: int | None
    content_type: str | None
    response_time_ms: int | None
    raw_html: str | None
    raw_text: str | None
    extracted_text: str | None
    clean_text: str | None
    markdown: str | None
    language: str | None
    crawled_at: datetime | None
    metadata: dict
```

Nếu hệ thống crawler không cung cấp tất cả field thì để `None`.

QA engine không được phụ thuộc trực tiếp vào schema gốc của crawler.

Phải có `mapper.py` để chuyển từ crawler schema sang `CrawledPage`.

---

# 8. Chuẩn lỗi QA

Mỗi lỗi phải theo schema:

```python
class QAError:
    error_code: str
    category: str
    severity: str
    page_id: str | None
    source_id: str
    url: str | None
    message: str
    metric: str | None
    observed_value: float | str | None
    threshold: float | str | None
    recommended_action: str | None
    evidence: dict | None
```

Severity:

```text
INFO
WARNING
ERROR
CRITICAL
```

Không dùng duy nhất một `quality_score` để thay cho chi tiết lỗi.

---

# 9. Bộ lỗi cần kiểm tra trong MVP

## 9.1. HTTP / network

### HTTP_4XX

Flag khi status code nằm trong 400–499.

Tách riêng:

```text
HTTP_401
HTTP_403
HTTP_404
HTTP_408
HTTP_429
```

### HTTP_5XX

```text
HTTP_500
HTTP_502
HTTP_503
HTTP_504
```

### REDIRECT_LOOP

Nếu có redirect chain lặp.

### TOO_MANY_REDIRECTS

Nếu redirect vượt threshold, mặc định 10.

### REQUEST_TIMEOUT

Nếu crawler có metadata timeout hoặc response time vượt ngưỡng.

---

# 10. Auth / access related errors

## AUTH_REDIRECT_TO_LOGIN

Requested URL là page content nhưng `final_url` chuyển về `/login`, `/signin`, `/auth`.

## AUTH_LOGIN_PAGE_RETURNED

HTTP 200 nhưng nội dung là trang đăng nhập.

Dấu hiệu:

```text
sign in
log in
email
password
forgot password
```

Kết hợp DOM form để giảm false positive.

## AUTH_SESSION_EXPIRED

Nếu một batch đầu đọc được content nhưng batch sau trả login page.

---

# 11. Empty / low-content errors

## EMPTY_PAGE

```text
status=200
AND extracted_text length = 0
```

## VERY_LOW_CONTENT

Mặc định:

```text
word_count < 20
```

Nhưng chỉ là warning, không mặc định coi là invalid.

## SUSPICIOUS_SHORT_PAGE

Dùng per-source distribution.

Ví dụ:

```text
text length < P1 hoặc < Q1 - 1.5*IQR
```

---

# 12. Soft 404

## SOFT_404

HTTP 200 nhưng content cho thấy page không tồn tại.

Keyword đa ngôn ngữ cơ bản:

```text
404
not found
page not found
content not found
không tìm thấy
trang không tồn tại
nội dung không tồn tại
```

Không chỉ check keyword. Nên kết hợp:

- title;
- heading h1;
- body text;
- content length;
- similarity với known 404 template.

---

# 13. CAPTCHA / anti-bot

## CAPTCHA_PAGE

Dấu hiệu:

```text
captcha
verify you are human
recaptcha
hcaptcha
```

## ANTI_BOT_PAGE

Dấu hiệu:

```text
checking your browser
access denied
attention required
cloudflare
bot detection
```

Nếu có raw HTML, kiểm tra các signature tương ứng.

---

# 14. JS rendering error

## POSSIBLE_JS_RENDER_REQUIRED

Nếu:

```text
status = 200
raw_html tương đối lớn
nhưng extracted_text rất ngắn
```

hoặc raw HTML chứa nhiều script bundle nhưng body gần như trống.

Ví dụ:

```html
<div id="app"></div>
<script src="main.js"></script>
```

Nếu có rendered output và raw output, so sánh:

```text
rendered_text_len / raw_text_len
```

---

# 15. Encoding errors

## ENCODING_MOJIBAKE

Tìm các pattern:

```text
Ã
Â
â€™
â€œ
â€
```

## UNICODE_REPLACEMENT_CHAR

Flag nếu có ký tự:

```text
�
```

Tính tỷ lệ lỗi trên tổng ký tự.

---

# 16. Cleaning quality

Nếu hệ thống có raw/extracted/clean output thì phải kiểm tra retention.

## CLEANING_OVER_AGGRESSIVE

Metric:

```text
retention_ratio = len(clean_text) / len(extracted_text)
```

Không dùng threshold cố định duy nhất cho mọi site.

MVP warning mặc định:

```text
retention_ratio < 0.10
```

Sau đó dùng source profile.

## CLEANING_TOO_WEAK

Nếu clean text gần như bằng raw extracted text và source có nhiều boilerplate.

MVP heuristic:

```text
retention_ratio > 0.95
AND repeated_block_ratio cao
```

## CLEAN_RESULT_EMPTY

```text
extracted_text > 500 chars
AND clean_text == empty
```

Đây là ERROR.

---

# 17. Repeated / boilerplate content

Tool cần phân tích block lặp giữa nhiều page cùng source.

Chuẩn hóa block trước:

- lowercase;
- collapse whitespace;
- loại timestamp động;
- loại số ID nếu phù hợp;
- hash normalized block.

Nếu một block xuất hiện trên tỷ lệ lớn page, ví dụ >70%, có thể là boilerplate.

Các lỗi:

```text
HIGH_BOILERPLATE_RATIO
REPEATED_HEADER
REPEATED_FOOTER
NAVIGATION_HEAVY
```

Không xóa tự động trong MVP. Chỉ flag và báo evidence.

---

# 18. Duplicate detection

## EXACT_DUPLICATE_CONTENT

Hash normalized content.

Khuyến nghị SHA-256.

## NEAR_DUPLICATE_CONTENT

Có thể dùng:

- SimHash;
- MinHash;
- Jaccard token shingles.

MVP có thể dùng SimHash hoặc MinHash.

Output nhóm duplicate:

```json
{
  "group_id": "dup_001",
  "pages": ["p1", "p2", "p3"],
  "similarity": 0.96
}
```

Không cần so sánh O(n²) toàn bộ page nếu source lớn.

Dùng LSH/indexing.

---

# 19. URL quality

Các rule:

```text
DUPLICATE_URL
TRACKING_PARAM_PRESENT
URL_FRAGMENT_DUPLICATION
SUSPICIOUS_PAGINATION_TRAP
SUSPICIOUS_CALENDAR_TRAP
QUERY_PARAM_EXPLOSION
```

Normalize các params phổ biến:

```text
utm_source
utm_medium
utm_campaign
utm_term
utm_content
fbclid
gclid
```

Không tự strip mọi query param vì một số param là business key thật.

---

# 20. MIME / content type

## CONTENT_TYPE_MISMATCH

Ví dụ URL tưởng HTML nhưng trả PDF/JSON/image.

## HTML_EXPECTED_BUT_BINARY

Nếu extractor HTML nhận binary.

## PDF_TRUNCATED

Nếu metadata có `Content-Length` và actual bytes nhỏ hơn đáng kể.

---

# 21. Language mismatch

Nếu source kỳ vọng ngôn ngữ nhất định, tool có thể detect language.

Các lỗi:

```text
LANGUAGE_MISMATCH
UNKNOWN_LANGUAGE
MIXED_LANGUAGE_SUSPICIOUS
```

Không bắt buộc trong MVP đầu tiên nếu chưa có dependency phù hợp.

---

# 22. Metadata / schema validation

Các field tối thiểu:

```text
page_id
source_id
url
```

Nếu có:

```text
status_code
crawled_at
content
```

thì validate type.

Các lỗi:

```text
MISSING_REQUIRED_FIELD
INVALID_STATUS_CODE
INVALID_TIMESTAMP
FUTURE_TIMESTAMP
EMPTY_URL
INVALID_URL
```

---

# 23. Statistical source profile

Tool phải có khái niệm `Source Profile`.

Mỗi source sau lần scan đầu nên lưu:

```text
page_count
status distribution
median text length
P5/P25/P50/P75/P95/P99
word count distribution
link density distribution
retention ratio distribution
language distribution
content type distribution
common blocks
common title patterns
common URL patterns
```

Profile này dùng để detect anomaly tốt hơn rule cứng.

Cache profile theo:

```text
source_id + crawl_version/job_id
```

Nếu source có crawl mới thì profile cần invalidate hoặc version hóa.

---

# 24. Anomaly detection

MVP dùng IQR/percentile trước.

Ví dụ:

```text
Q1 = 1500 chars
Q3 = 7000 chars
IQR = 5500
lower = max(0, Q1 - 1.5*IQR)
upper = Q3 + 1.5*IQR
```

Flag page nằm quá xa distribution.

Sau này có thể thêm:

```text
Isolation Forest
LOF
Robust Z-score
```

Không cần ML phức tạp ở version đầu.

---

# 25. QA Engine architecture

Mỗi rule phải độc lập.

Pseudo-interface:

```python
class QARule(Protocol):
    code: str
    category: str

    def evaluate(self, page: CrawledPage, context: QAContext) -> list[QAError]:
        ...
```

Registry:

```python
RULES = [
    Http404Rule(),
    Soft404Rule(),
    EmptyPageRule(),
    CaptchaRule(),
    EncodingRule(),
    CleaningRetentionRule(),
]
```

Không viết tất cả logic vào một function lớn.

---

# 26. QA Context

Một số rule cần context toàn source.

Ví dụ:

```python
class QAContext:
    source_profile: SourceProfile
    duplicate_index: object
    common_blocks: set[str]
    config: QAConfig
```

Rule page-level không cần query DB lại nhiều lần.

---

# 27. Chế độ chạy

Tool cần tối thiểu 3 mode.

## Single Page

User chọn một page.

Chạy rule page-level.

Không chạy các rule cần statistics toàn source nếu chưa có profile.

## Sample Source

User chọn sample N page:

```text
50
100
500
```

Dùng để test nhanh.

## Whole Source

Chạy toàn source.

Phải build/reuse source profile.

Đây là mode chuẩn để đánh giá chất lượng export thực tế.

---

# 28. Dashboard yêu cầu

Trang Overview nên hiển thị:

```text
Total pages
Passed pages
Pages with warnings
Pages with errors
Critical pages
```

Phân bố status:

```text
2xx
3xx
4xx
5xx
```

Top lỗi:

```text
SOFT_404
EMPTY_PAGE
DUPLICATE
CAPTCHA
CLEANING_OVER_AGGRESSIVE
ENCODING_MOJIBAKE
```

Có filter theo:

```text
source
job
severity
error_code
status_code
URL keyword
```

---

# 29. Page detail view

Khi click vào một page, hiển thị:

```text
URL
final URL
status code
crawl time
response time
content type
word count
char count
```

Phần nội dung nên có tab:

```text
Raw HTML
Raw text
Extracted
Cleaned
Markdown
Errors
```

Nếu không có field nào thì ẩn tab đó.

---

# 30. Diff viewer

Một feature rất nên có:

```text
Extracted vs Cleaned
```

Highlight:

- text bị xóa;
- text được giữ;
- block lặp;
- block nghi boilerplate.

MVP có thể dùng text diff line-based.

Sau này nâng cấp block-based diff.

---

# 31. Export QA results

Hỗ trợ:

```text
CSV
JSON
Parquet
```

Schema export đề xuất:

```text
source_id
page_id
url
status_code
severity
error_code
category
message
observed_value
threshold
recommended_action
```

Một page có nhiều lỗi thì có nhiều row.

Ngoài ra tạo summary export:

```text
source_summary.csv
```

với:

```text
source_id
page_count
error_pages
warning_pages
critical_pages
exact_duplicate_rate
near_duplicate_rate
soft_404_rate
empty_rate
```

---

# 32. Parquet support

Nếu crawler hỗ trợ export Parquet, tool nên đọc trực tiếp.

Ví dụ:

```python
import pandas as pd

df = pd.read_parquet("dataset.parquet")
```

Nếu file rất lớn, ưu tiên `pyarrow.dataset` hoặc đọc row group.

Không convert sang CSV trước khi phân tích nếu không cần thiết.

---

# 33. Performance

Không tải full HTML của toàn bộ hàng trăm nghìn page ngay từ đầu nếu API có metadata endpoint.

Luồng khuyến nghị:

```text
1. fetch page metadata
2. run cheap checks
3. identify suspicious pages
4. fetch full content cho suspicious pages
5. run expensive checks
```

Các expensive checks:

```text
near duplicate
DOM analysis
LLM inspection
large text diff
```

---

# 34. Pagination

Crawler API có thể dùng:

```text
page/page_size
limit/offset
cursor
next_token
```

Client phải hỗ trợ pagination abstract.

Không assume `page=1` nếu chưa xác nhận.

---

# 35. Rate limiting

QA tool không được làm quá tải crawler backend.

Config:

```env
QA_MAX_CONCURRENCY=10
QA_REQUEST_TIMEOUT=30
QA_RETRY_COUNT=3
```

Retry cho:

```text
408
429
502
503
504
network timeout
```

Dùng exponential backoff.

Không retry vô hạn.

---

# 36. Logging

Log cần structured.

Ví dụ:

```json
{
  "event": "page_qa_finished",
  "source_id": "s1",
  "page_id": "p123",
  "errors": 2,
  "duration_ms": 34
}
```

Không log:

```text
password
full auth token
session cookie
```

Mask token nếu cần debug:

```text
abc123...xyz
```

---

# 37. Security

Các nguyên tắc bắt buộc:

- Credentials chỉ đọc từ env/secret.
- Không commit token/password.
- Không hiển thị password trong UI/log.
- Nếu lưu session cookie thì file phải nằm ngoài Git.
- API key của QA tool nên read-only.
- Không có chức năng delete/update dữ liệu crawler trong MVP.
- QA tool mặc định chỉ GET/read.
- Nếu có browser storage state thì giới hạn quyền file.

---

# 38. Error handling

Nếu login fail:

```text
AUTH_FAILED
```

Hiển thị nguyên nhân nếu biết:

```text
invalid credentials
CSRF required
2FA required
session expired
endpoint changed
```

Nếu API schema thay đổi:

```text
UPSTREAM_SCHEMA_CHANGED
```

Không crash toàn bộ job vì một page lỗi.

Mỗi page phải được xử lý độc lập.

---

# 39. Unit test tối thiểu

Phải có test cho:

```text
404 detection
soft 404 detection
captcha detection
login page detection
encoding mojibake
empty page
cleaning retention
exact duplicate
URL normalization
```

Fixtures nên đặt trong:

```text
tests/fixtures/
```

Ví dụ:

```text
normal_article.html
soft_404.html
captcha.html
login.html
empty.html
mojibake.html
```

---

# 40. Integration test

Sau khi có credentials thực:

1. login;
2. list sources;
3. lấy 1 source;
4. lấy 10 page;
5. normalize schema;
6. chạy QA;
7. export result.

Không test destructive action.

---

# 41. Acceptance criteria cho MVP

MVP được xem là hoàn thành khi:

- Login/access được crawler platform.
- List được source.
- List/fetch được page đã crawl.
- Chuẩn hóa được page về schema nội bộ.
- Chạy được tối thiểu 15 rule QA.
- Có source overview.
- Có page error list.
- Có page detail.
- Có filter theo error/severity.
- Có export CSV/JSON/Parquet.
- Không hard-code credentials.
- Có unit tests.
- Có README hướng dẫn setup/run.

---

# 42. Danh sách 15 rule bắt buộc cho MVP

```text
HTTP_404
HTTP_429
HTTP_5XX
AUTH_REDIRECT_TO_LOGIN
AUTH_LOGIN_PAGE_RETURNED
EMPTY_PAGE
VERY_LOW_CONTENT
SOFT_404
CAPTCHA_PAGE
ANTI_BOT_PAGE
ENCODING_MOJIBAKE
UNICODE_REPLACEMENT_CHAR
CLEAN_RESULT_EMPTY
CLEANING_OVER_AGGRESSIVE
EXACT_DUPLICATE_CONTENT
```

Ưu tiên implement chắc 15 rule này trước khi mở rộng.

---

# 43. Phase 2

Sau MVP thêm:

```text
Near duplicate
Source profile
Boilerplate frequency
Navigation density
JS render detection
Language detection
URL crawl trap detection
Content type mismatch
Timestamp anomalies
IQR anomaly detection
```

---

# 44. Phase 3

Có thể thêm semantic QA:

```text
Title-content relevance
Embedding similarity
Topic mismatch
Content coherence
Chunk quality
```

Không chạy embedding/LLM trên mọi page ngay từ đầu.

Chỉ chạy trên sample hoặc suspicious subset.

---

# 45. Optional LLM inspection

Flow:

```text
Rule based
    ↓
Statistical detection
    ↓
Suspicious pages
    ↓
LLM classifier
```

LLM có thể classify:

```text
NORMAL_CONTENT
LOGIN_PAGE
CAPTCHA
SOFT_404
NAVIGATION
BOILERPLATE
SPAM
BROKEN_EXTRACTION
```

Không để LLM là tầng kiểm tra duy nhất.

---

# 46. Recommended actions mapping

Mỗi lỗi nên có hướng xử lý.

Ví dụ:

```text
HTTP_429
→ giảm concurrency/rate

CAPTCHA_PAGE
→ kiểm tra anti-bot hoặc authenticated/browser crawl

AUTH_LOGIN_PAGE_RETURNED
→ refresh session / login lại

CLEANING_OVER_AGGRESSIVE
→ giảm mức cleaning hoặc kiểm tra rule removal

EXACT_DUPLICATE_CONTENT
→ canonicalize/dedupe

ENCODING_MOJIBAKE
→ kiểm tra charset detection/decode
```

---

# 47. Không nên làm trong MVP

Không ưu tiên:

- auto delete page lỗi;
- auto sửa trực tiếp dữ liệu production;
- auto rotate proxy;
- auto crawl lại hàng loạt;
- auto login CAPTCHA bypass;
- LLM cho toàn dataset;
- machine learning phức tạp.

Mục tiêu đầu tiên là **quan sát chính xác và giải thích được lỗi**.

---

# 48. CLI đề xuất

Có thể hỗ trợ:

```bash
python -m app.cli auth-test
python -m app.cli list-sources
python -m app.cli scan-source SOURCE_ID
python -m app.cli scan-page PAGE_ID
python -m app.cli export SOURCE_ID --format parquet
```

CLI giúp debug trước khi làm UI hoàn chỉnh.

---

# 49. API nội bộ của QA Tool

Đề xuất:

```http
GET /health
GET /sources
GET /sources/{id}
GET /sources/{id}/pages
POST /sources/{id}/scan
GET /scans/{scan_id}
GET /scans/{scan_id}/errors
GET /pages/{page_id}
GET /pages/{page_id}/errors
GET /pages/{page_id}/diff
POST /exports
```

---

# 50. Scan persistence

Lưu mỗi lần scan:

```text
scan_id
source_id
job_id
started_at
finished_at
status
rule_version
profile_version
page_count
error_count
```

Điều này cho phép so sánh chất lượng giữa nhiều lần crawl.

---

# 51. So sánh các lần crawl

Phase 2 nên hỗ trợ:

```text
crawl job A vs crawl job B
```

Metrics:

```text
page count change
404 rate change
empty rate change
duplicate rate change
clean retention change
```

Ví dụ:

```text
Job 101
empty pages: 1.2%

Job 102
empty pages: 14.8%
```

→ regression rõ ràng.

---

# 52. Regression detection

Có thể tạo warning:

```text
ERROR_RATE_REGRESSION
CONTENT_LENGTH_REGRESSION
DUPLICATE_RATE_REGRESSION
CLEANING_REGRESSION
```

Rule so sánh với previous successful job.

---

# 53. Cách agent nên triển khai

Thứ tự implementation đề xuất:

```text
Step 1  - bootstrap project
Step 2  - config/env
Step 3  - auth discovery
Step 4  - crawler client
Step 5  - schema mapper
Step 6  - CLI list-source/list-page
Step 7  - QA rule framework
Step 8  - 15 MVP rules
Step 9  - source scan
Step 10 - persistence
Step 11 - export
Step 12 - web dashboard
Step 13 - tests
Step 14 - docs
```

Không bắt đầu bằng frontend trước khi crawler access và QA engine chạy ổn.

---

# 54. Khi credentials được cung cấp

Sau khi nhận email/password:

1. điền vào `.env` cục bộ;
2. chạy auth discovery;
3. xác định endpoint login;
4. xác định API list source;
5. xác định API page/content;
6. lưu observed API docs;
7. implement production auth adapter;
8. chạy integration test với sample nhỏ;
9. không scan toàn bộ source ngay lập tức;
10. chỉ chạy whole source khi sample hoạt động ổn.

---

# 55. Definition of Done

Tool được xem là usable khi một người dùng có thể:

```text
1. cấu hình credentials
2. mở QA tool
3. chọn một crawler source
4. bấm Scan
5. xem số page lỗi
6. filter theo loại lỗi
7. mở một page lỗi
8. xem raw/cleaned content và evidence
9. hiểu vì sao page bị flag
10. export kết quả
```

Mỗi lỗi phải **giải thích được**, không chỉ trả về một điểm số mơ hồ.

---

# 56. Ghi chú cuối cho agent

- Không giả định API crawler nếu chưa kiểm tra network/API thực tế.
- Không hard-code credentials.
- Không dùng browser automation nếu API đã đủ dùng.
- Không dùng một threshold cố định cho mọi website nếu có thể dùng source profile.
- Không để một page lỗi làm chết toàn scan.
- Không chạy near-duplicate O(n²) trên source lớn.
- Không log secret.
- Ưu tiên read-only integration.
- Giữ rule engine modular.
- Mỗi rule phải có test.
- Mỗi error code phải có mô tả và recommended action.

Mục tiêu của sản phẩm không chỉ là nói **“page này lỗi”**, mà phải trả lời được:

```text
Lỗi gì?
Phát hiện bằng bằng chứng nào?
Mức độ nghiêm trọng ra sao?
Lỗi nằm ở crawl, extraction hay cleaning?
Nên kiểm tra/sửa bước nào tiếp theo?
```

Đó là tiêu chuẩn chính của Web Crawl QA Tool.
