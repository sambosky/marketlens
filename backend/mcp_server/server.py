"""MarketLens MCP server (the external add-on).

Re-exposes the same skill functions the app uses internally, plus a top-level
``ask_marketlens`` tool that runs the full ADK pipeline and returns a cited
answer — so the whole assistant can be used as a tool inside Claude Desktop /
Cursor. Runs over stdio.

Run::

    python -m mcp_server.server
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from agents.runner import MarketLensAgent
from infra.container import make_container
from skills.adk_tools import SKILL_FUNCTIONS, bind_container

_container = make_container()
_agent: MarketLensAgent | None = None


@asynccontextmanager
async def _lifespan(_server: FastMCP):
    bind_container(_container)
    try:
        yield {}
    finally:
        await _container.close()


mcp = FastMCP("marketlens", lifespan=_lifespan)

# Register every skill as an MCP tool (schemas derived from the typed signatures).
for _fn in SKILL_FUNCTIONS:
    mcp.add_tool(_fn)


@mcp.tool()
async def ask_marketlens(question: str) -> dict:
    """Ask MarketLens a stock-research question and get a cited, non-advisory
    answer (routes across SEC filings, news, live prices, and the demo
    portfolio). This is research, not financial advice."""
    global _agent
    if _agent is None:
        from google.adk.models.lite_llm import LiteLlm

        llm = await _container.get(LiteLlm)
        _agent = MarketLensAgent(llm)
    return await _agent.ask(question)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
