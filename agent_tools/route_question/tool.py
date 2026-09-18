"""Deterministic routing for recurring crawler inspection questions."""

from __future__ import annotations

from typing import Any

from ..registry import ToolRegistry


def route_question(question: str) -> dict[str, Any]:
    text = question.casefold()
    registry = ToolRegistry()
    if any(marker in text for marker in ("báo cáo", "report", "export", "ghi log", "log lỗi", "thống kê lỗi", "tổng hợp", "cộng dồn", "từ đầu đến giờ", "summary", "gửi cho dev")):
        return {"tool_name": "export_crawler_error_report", "reason": "Question asks to aggregate crawler errors into a shareable report."}
    if any(marker in text for marker in ("lịch sử", "history", "audit", "các lần crawl", "ngày 16", "ngày 17")) and any(marker in text for marker in ("foody", "pytorch", "source", "job")):
        return {"tool_name": "audit_crawl_history", "reason": "Question asks for a historical multi-job/source failure audit."}
    if "404" in text and any(marker in text for marker in ("url", "path", "version", "crawler", "document", "tài liệu", "đường dẫn")):
        return {"tool_name": "diagnose_url_404_mismatch", "reason": "Question compares a crawler 404 URL with a current upstream document URL."}
    if any(
        marker in text
        for marker in (
            "ngoài source",
            "ngoài phạm vi",
            "không liên quan",
            "out of scope",
            "scope leak",
            "external domain",
            "external url",
            "microsoft learn",
            "twitter",
        )
    ) and any(marker in text for marker in ("crawl", "crawler", "source", "job", "page", "link", "url")):
        return {"tool_name": "diagnose_out_of_scope_urls", "reason": "Question asks why a crawl produced pages or links outside the source scope."}
    if any(marker in text for marker in ("system gave up", "failed", "failure", "thất bại", "lỗi", "crw_permanent", "js_escalation")):
        return {"tool_name": "diagnose_failed_pages", "reason": "Question mentions systematic page failures or upstream failure signatures."}
    if any(marker in text for marker in ("chạy mãi", "stuck", "queue", "budget", "loop url", "loop", "không dừng")):
        return {"tool_name": "diagnose_crawl_stall", "reason": "Question mentions job liveness, budget or URL loop."}
    if "raw" in text and any(marker in text for marker in ("preview", "giống", "provenance")):
        return {"tool_name": "check_raw_provenance", "reason": "Question compares page view and RAW preview artifacts."}
    if any(marker in text for marker in ("safe", "clean", "làm sạch", "input", "light", "heavy")):
        if any(marker in text for marker in ("dài hơn", "longer", "length", "ký tự")):
            return {"tool_name": "explain_clean_output_length", "reason": "Question asks about clean output size."}
        return {"tool_name": "compare_clean_modes", "reason": "Question compares clean modes."}
    if any(marker in text for marker in ("text/html", "xếp vào resource", "phân loại")):
        return {"tool_name": "explain_page_classification", "reason": "Question asks about page/resource classification."}
    if any(marker in text for marker in ("resource", "png", "svg", "ảnh", "css", "javascript", "asset")):
        return {"tool_name": "analyze_resource_mix", "reason": "Question asks why resources dominate or what types they contain."}
    if any(marker in text for marker in ("navigation", "kind", "xếp")):
        return {"tool_name": "explain_page_classification", "reason": "Question asks about page/resource classification."}
    return registry.propose(question, "No registered tool matched the question capability.").to_dict()
