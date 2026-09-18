from __future__ import annotations

from agent_tools.models import ToolResult
from agent_tools.registry import ToolRegistry


def test_tool_result_is_structured_and_read_only_by_default():
    result = ToolResult(
        tool_name="inspect_job",
        answer="Job is running.",
        evidence=[{"field": "status", "observed": "RUNNING"}],
        metrics={"in_queue": 2},
        recommended_actions=["Inspect queue progress."],
    )

    assert result.read_only is True
    assert result.to_dict()["tool_name"] == "inspect_job"
    assert result.to_dict()["evidence"][0]["observed"] == "RUNNING"


def test_registry_runs_registered_tool_without_exposing_secrets():
    registry = ToolRegistry()
    registry.register("echo", "Echo safe input", lambda value: ToolResult("echo", value))

    result = registry.run("echo", value="status only")

    assert result.tool_name == "echo"
    assert result.answer == "status only"
    assert "password" not in result.to_dict()


def test_registry_returns_new_tool_proposal_for_unknown_tool():
    registry = ToolRegistry()

    result = registry.propose("Why is the crawler stuck?", "No registered diagnostic covers queue liveness")

    assert result.tool_name == "tool_proposal"
    assert result.new_tool_proposal["question"] == "Why is the crawler stuck?"
    assert result.read_only is True
