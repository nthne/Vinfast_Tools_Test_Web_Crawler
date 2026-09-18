from __future__ import annotations

from agent_tools.check_raw_provenance import check_raw_provenance
from agent_tools.compare_clean_modes import compare_clean_modes
from agent_tools.explain_clean_output_length import explain_clean_output_length
from agent_tools.inspect_export_cleaning import inspect_export_cleaning


class FakeCleaningClient:
    def list_clean_modes(self):
        return {"items": [{"mode": "RAW"}, {"mode": "LIGHT"}, {"mode": "HEAVY"}, {"mode": "SAFE"}], "llm_ready": True}

    def preview_clean(self, page_id, clean_mode, scope="PAGE"):
        values = {
            "RAW": (80, 80, False, []),
            "LIGHT": (80, 40, False, []),
            "HEAVY": (80, 40, False, ["LLM unavailable; fell back to LIGHT"]),
            "SAFE": (80, 82, False, []),
        }
        original, kept, reverted, degraded = values[clean_mode]
        return {
            "crawl_page_id": page_id,
            "clean_mode": clean_mode,
            "scope": scope,
            "matches_export": False,
            "original_characters": original,
            "kept_characters": kept,
            "reverted": reverted,
            "degraded": degraded,
            "markdown": "x" * kept,
        }

    def get_page_view(self, page_id):
        return {"crawl_page_id": page_id, "markdown": "x" * 100, "content_type": "text/html"}

    def list_exports(self, limit=None):
        return [
            {
                "id": "export-1",
                "status": "COMPLETED",
                "params": {"clean_mode": "HEAVY"},
                "cleaning": {"mode": "HEAVY", "pages_cleaned": 10, "characters_before": 1000, "characters_after": 500, "degraded": ["fell back to LIGHT"]},
            }
        ]


def test_compare_clean_modes_returns_retention_for_each_mode():
    result = compare_clean_modes(FakeCleaningClient(), "p-1")

    assert result.metrics["modes"]["LIGHT"]["retention_ratio"] == 0.5
    assert result.metrics["modes"]["HEAVY"]["degraded"] is True


def test_explain_clean_output_length_flags_small_output_expansion():
    result = explain_clean_output_length(FakeCleaningClient(), "p-1", "SAFE")

    assert result.metrics["original_characters"] == 80
    assert result.metrics["kept_characters"] == 82
    assert result.metrics["retention_ratio"] == 1.025
    assert "CLEAN_OUTPUT_EXPANDED" in result.warnings


def test_check_raw_provenance_detects_different_page_view_input():
    result = check_raw_provenance(FakeCleaningClient(), "p-1")

    assert result.metrics["page_view_characters"] == 100
    assert result.metrics["clean_preview_raw_characters"] == 80
    assert "CLEAN_PREVIEW_INPUT_MISMATCH" in result.warnings
    assert "CLEAN_PREVIEW_EXPORT_MISMATCH" in result.warnings


def test_inspect_export_cleaning_surfaces_degraded_export():
    result = inspect_export_cleaning(FakeCleaningClient())

    assert result.metrics["export_count"] == 1
    assert result.metrics["degraded_export_count"] == 1
    assert "CLEAN_MODE_DEGRADED" in result.warnings
