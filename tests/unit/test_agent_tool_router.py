from __future__ import annotations

from agent_tools.router import route_question


def test_router_maps_crawl_stall_question_to_diagnostic_tool():
    routed = route_question("Vì sao job chạy mãi, vượt budget và có thể loop URL?")

    assert routed["tool_name"] == "diagnose_crawl_stall"


def test_router_maps_resource_question_to_resource_mix_tool():
    routed = route_question("Tại sao resource hầu hết là ảnh png/svg?")

    assert routed["tool_name"] == "analyze_resource_mix"


def test_router_maps_out_of_scope_page_question_to_scope_leak_tool():
    routed = route_question("Tại sao Foody crawl ra Microsoft Learn và Twitter ngoài source ban đầu?")

    assert routed["tool_name"] == "diagnose_out_of_scope_urls"


def test_router_prioritizes_classification_for_html_resource_question():
    routed = route_question("Tại sao text/html bị xếp vào resource?")

    assert routed["tool_name"] == "explain_page_classification"


def test_router_maps_clean_and_provenance_questions():
    assert route_question("Tại sao SAFE dài hơn input?")["tool_name"] == "explain_clean_output_length"
    assert route_question("RAW preview có giống raw không?")["tool_name"] == "check_raw_provenance"


def test_router_returns_proposal_for_uncovered_question():
    routed = route_question("So sánh chất lượng ngôn ngữ giữa hai crawl job")

    assert routed["tool_name"] == "tool_proposal"
    assert routed["new_tool_proposal"]["read_only"] is True


def test_router_maps_upstream_url_404_mismatch_question():
    routed = route_question(
        "URL hiện tại của tài liệu PyTorch hợp lệ nhưng URL crawler lấy bị 404, kiểm tra path/version"
    )

    assert routed["tool_name"] == "diagnose_url_404_mismatch"


def test_router_prioritizes_url_404_mismatch_over_generic_failure_wording():
    routed = route_question(
        "Đây là lỗi do PyTorch hay hạn chế của web crawler khi URL crawler bị 404?"
    )

    assert routed["tool_name"] == "diagnose_url_404_mismatch"


def test_router_maps_historical_multi_source_audit_question():
    routed = route_question(
        "Kiểm tra lịch sử tất cả lỗi fail của Foody và Pytorch trong các lần crawl ngày 16 và 17/9"
    )

    assert routed["tool_name"] == "audit_crawl_history"


def test_router_accepts_normal_utf8_vietnamese_questions():
    assert route_question("Tại sao job chạy mãi và vượt page budget?")["tool_name"] == "diagnose_crawl_stall"
    assert route_question("Tại sao text/html bị xếp vào resource?")["tool_name"] == "explain_page_classification"
    assert route_question("Tại sao SAFE dài hơn input?")["tool_name"] == "explain_clean_output_length"
    assert route_question("Why is SAFE output longer than input?")["tool_name"] == "explain_clean_output_length"
    assert route_question("Tại sao tất cả page đều failed với lỗi The system gave up?")["tool_name"] == "diagnose_failed_pages"
    assert route_question("Thống kê lỗi crawl vào một file để gửi cho dev")["tool_name"] == "export_crawler_error_report"
    assert route_question("Tạo một file tổng hợp các lỗi từ đầu đến giờ")["tool_name"] == "export_crawler_error_report"


def test_default_registry_forwards_resource_sample_page_size():
    from agent_tools.router import default_registry

    class EmptyClient:
        def list_pages(self, **kwargs):
            return []

    result = default_registry(EmptyClient()).run(
        "analyze_resource_mix", job_id="job-1", sample_pages=1, page_size=7
    )

    assert result.metrics["sample_count"] == 0
