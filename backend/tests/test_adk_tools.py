"""The tool registry that powers ADK, the /tools API, and MCP."""

from __future__ import annotations

from skills import adk_tools
from skills.types import SkillResult


class FakeSkill:
    async def run(self, *args, **kwargs) -> SkillResult:
        return SkillResult(skill="get_quote", summary="ok")


class FakeContainer:
    async def get(self, _cls) -> FakeSkill:
        return FakeSkill()


def test_tool_schemas_lists_every_skill():
    names = {t["name"] for t in adk_tools.tool_schemas()}
    expected = {
        "search_filings",
        "search_news",
        "get_quote",
        "get_portfolio",
        "add_to_watchlist",
        "list_watchlist",
        "set_price_alert",
        "list_alerts",
        "log_trade",
        "list_journal",
    }
    assert expected <= names


def test_tool_schema_marks_required_params():
    schema = next(t for t in adk_tools.tool_schemas() if t["name"] == "get_quote")
    assert schema["parameters"]["ticker"]["required"] is True


async def test_call_tool_dispatches_to_skill():
    adk_tools.bind_container(FakeContainer())  # type: ignore[arg-type]
    out = await adk_tools.call_tool("get_quote", {"ticker": "AAPL"})
    assert out["skill"] == "get_quote"


async def test_call_tool_unknown_raises():
    import pytest

    with pytest.raises(KeyError):
        await adk_tools.call_tool("does_not_exist", {})
