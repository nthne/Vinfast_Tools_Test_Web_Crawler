# Web Crawl QA Agent Toolkit

Bộ công cụ read-only để agent kiểm tra chất lượng và hành vi của dữ liệu web crawler đã chạy. Project này không phải crawler chính và cũng không ưu tiên xây một web dashboard độc lập.

Repository GitHub: [nthne/Vinfast_Tools_Test_Web_Crawler](https://github.com/nthne/Vinfast_Tools_Test_Web_Crawler)

Repository này là project `test_web_crawler`, gồm các tool kiểm tra source/job/page, phân tích resource và page classification, đối chiếu clean output, chẩn đoán crawl stall/failed pages/scope leak/404 mismatch, audit lịch sử crawl và xuất error report. Repository cũng chứa unit tests, API observations, tool contracts và các báo cáo kiểm thử crawler chi tiết. Thư mục `huong_dan` không thuộc repository này.

Mục tiêu là để agent trả lời được các câu hỏi như:

- Vì sao job chạy mãi hoặc không dừng sau khi chạm budget?
- Có phải crawler bị URL loop, URL expansion hoặc resource trap không?
- Vì sao resource chủ yếu là ảnh, CSS hoặc SVG?
- Vì sao URL `.png`/`.svg` lại trả `text/html`?
- Vì sao `SAFE` output dài hơn input?
- RAW trong clean preview có giống raw/page view không?
- HEAVY có thực sự dùng LLM hay đã fallback về LIGHT?

## Nguyên tắc phát triển

Mỗi câu hỏi kiểm tra lặp lại phải được chuyển thành một tool có:

```text
tool name
input schema
read-only client calls
observed evidence
metrics
hypotheses
recommended actions
confidence
```

Nếu câu hỏi chưa có tool phù hợp, router không tự gọi endpoint mutation. Nó trả về `tool_proposal` để agent đề xuất capability mới, sau đó ghi contract và test cho tool được duyệt.

Credentials chỉ đọc từ environment/secret manager. Không đưa password, token, cookie hoặc signed URL vào tool input/output/log.

## Tool hiện có

| Tool | Mục đích |
|---|---|
| `inspect_source` | Đọc source URL, domain, enabled state, crawl config và rules |
| `inspect_job` | Đọc job status, counter, runtime budget và timestamps |
| `inspect_page` | Đọc page metadata, MIME, route, warning và độ dài content |
| `analyze_resource_mix` | Phân tích navigation/resource, image/CSS/JS/HTML, host ngoài và budget |
| `explain_page_classification` | Giải thích `NAVIGATION`/`RESOURCE` độc lập với response MIME |
| `compare_clean_modes` | So sánh RAW/LIGHT/HEAVY/SAFE |
| `explain_clean_output_length` | Giải thích retention ratio và output expansion |
| `check_raw_provenance` | Đối chiếu page view, RAW preview và export provenance |
| `inspect_export_cleaning` | Đọc cleaning report của các export hiện có |
| `diagnose_crawl_stall` | Chẩn đoán budget exhaustion, queue stall và URL expansion |
| `diagnose_failed_pages` | Phân biệt lỗi HTTP/site với lỗi renderer/CDP diện rộng |
| `diagnose_out_of_scope_urls` | Tìm page/link ngoài scope, resource HTML bị follow và sai lệch kind/MIME |
| `diagnose_url_404_mismatch` | Đối chiếu URL 404 của crawler với document URL hiện tại |
| `audit_crawl_history` | Audit lịch sử nhiều job/source và giải thích nhóm nguyên nhân lỗi |
| `export_crawler_error_report` | Ghi mỗi error signature thành report chi tiết và cập nhật summary cộng dồn |

Các tool được đăng ký qua:

```python
from agent_tools import default_registry, route_question

route = route_question("Tại sao job chạy mãi và có thể loop URL?")
# {"tool_name": "diagnose_crawl_stall", ...}

registry = default_registry(client)
result = registry.run(
    "diagnose_crawl_stall",
    job_id="JOB_ID",
    poll_seconds=10,
)
print(result.to_dict())
```

`result.to_dict()` không trả full page content và tự mask các key nhạy cảm.

## Kết nối crawler

Tạo `.env` local, không commit file này:

```env
CRAWLER_BASE_URL=https://crawler.example.internal
CRAWLER_EMAIL=...
CRAWLER_PASSWORD=...
CRAWLER_API_KEY=
CRAWLER_AUTH_MODE=auto
```

Không đặt credential thật trong `.env.example`; file example chỉ chứa placeholder.

Auth ưu tiên API key, sau đó login API/session. Browser/Playwright chỉ là boundary fallback cho hệ thống có JavaScript/SSO phức tạp. Tool mặc định chỉ gọi API GET; login POST chỉ dùng để tạo session.

## Dữ liệu local

Project vẫn hỗ trợ kiểm tra export Parquet/CSV/JSON thông qua `FileCrawlerClient`:

```python
from crawler_client.file_client import FileCrawlerClient

client = FileCrawlerClient("data_test/parquet/crawl-pages.parquet")
print(client.list_sources())
print(len(client.list_pages()))
```

Local sample hiện có 1.062 page của source Vinpearl.

## Cấu trúc chính

```text
/
  auth/                 Auth adapters
  crawler_client/       HTTP/local clients và schema mapper
  agent_tools/
    <tool_name>/
      tool.py           Implementation của một capability
      README.md         Contract, input, evidence và safety notes
    models.py           ToolResult dùng chung
    registry.py         Tool registry dùng chung
    router.py           Compatibility router và default registry
tests/unit/              Contract và behavior tests cho từng tool
docs/agent_tools.md      Tool catalog và tool proposal rules
data_test/               Local crawler export fixtures
```

## Verification

```powershell
python -m pytest -q
python -m compileall -q agent_tools auth crawler_client config.py
```

Live integration phải bắt đầu bằng source/job/page sample nhỏ. Không tự động run, cancel, delete, import, upload hoặc tạo export trên crawler production.

## Trạng thái phát triển

Đã có:

- config/auth/discovery/crawler clients;
- normalized page model;
- ToolResult và ToolRegistry;
- source/job/page/resource inspection tools;
- clean/provenance tools;
- crawl-stall/budget/URL-expansion diagnostic;
- systematic page-failure và renderer/CDP diagnostic;
- out-of-scope URL, external navigation và resource-HTML link-following diagnostic;
- deterministic question router và unknown-tool proposal.

Chưa có:

- 15 rule QA page-level đầy đủ;
- `diagnose_job_failure_root_cause` (đã ghi nhận contract, chờ duyệt triển khai);
- source profile/duplicate index;
- scan persistence SQLite;
- CSV/JSON/Parquet QA report exporter;
- FastAPI/CLI adapter cho toàn bộ tool catalog;
- dashboard web.

Hướng phát triển tiếp theo là hoàn thiện tool contracts và QA rules theo từng câu hỏi thực tế, sau đó mới thêm adapter CLI/API nếu cần. Chi tiết contract nằm trong [docs/agent_tools.md](docs/agent_tools.md) và kế hoạch tại [docs/superpowers/plans/2026-09-18-agent-tool-first-qa-plan.md](docs/superpowers/plans/2026-09-18-agent-tool-first-qa-plan.md).
