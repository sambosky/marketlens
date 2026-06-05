"""The skills exposed as callable tools.

This is the single source of truth used three ways:
  * the ADK agent loads them as ``FunctionTool``s (internal routing),
  * the ``/tools`` API lists + invokes them (the UI Tools panel),
  * the MCP server re-exposes them (Claude Desktop / Cursor).

Each function has a clean typed signature + docstring so ADK and MCP can derive
schemas automatically. They resolve their skill from the app-bound Dishka
container (APP-scoped, so a module reference is correct).
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from dishka import AsyncContainer

from skills.alerts import AlertsSkill
from skills.fundamentals import FundamentalsSkill
from skills.journal import JournalSkill
from skills.market_data import MarketDataSkill
from skills.news import NewsSkill
from skills.portfolio import PortfolioSkill
from skills.watchlist import WatchlistSkill

_container: AsyncContainer | None = None


def bind_container(container: AsyncContainer) -> None:
    """Bind the app container the tools resolve skills from (called at startup)."""
    global _container
    _container = container


def _c() -> AsyncContainer:
    if _container is None:
        raise RuntimeError("Tool container not bound — call bind_container() at startup.")
    return _container


def _split(tickers: str) -> list[str] | None:
    parsed = [t.strip().upper() for t in (tickers or "").split(",") if t.strip()]
    return parsed or None


# ── Research skills (cited RAG + live data) ───────────────────────────────────
async def search_filings(query: str, tickers: str = "") -> dict:
    """Search SEC filings (10-K/10-Q/8-K) for fundamentals: margins, revenue,
    segments, guidance, risk factors. `tickers` is an optional comma-separated
    filter, e.g. "NVDA,AAPL". Returns cited excerpts."""
    skill = await _c().get(FundamentalsSkill)
    return (await skill.run(query, tickers=_split(tickers))).as_dict()


async def search_news(query: str, tickers: str = "") -> dict:
    """Search recent news for catalysts / "why did it move?". `tickers` is an
    optional comma-separated filter. Returns cited excerpts."""
    skill = await _c().get(NewsSkill)
    return (await skill.run(query, tickers=_split(tickers))).as_dict()


async def get_quote(ticker: str) -> dict:
    """Get the live price, P/E, day range and market cap for one ticker."""
    skill = await _c().get(MarketDataSkill)
    return (await skill.run(ticker)).as_dict()


async def get_portfolio(ticker: str = "") -> dict:
    """Show the user's (demo) holdings marked to live prices. Pass a `ticker` to
    focus on one position, or leave empty for the whole portfolio."""
    skill = await _c().get(PortfolioSkill)
    return (await skill.run(ticker.strip().upper() or None)).as_dict()


# ── Action skills (non-executing) ─────────────────────────────────────────────
async def add_to_watchlist(ticker: str, note: str = "") -> dict:
    """Add a ticker to the watchlist (records locally; places no order)."""
    skill = await _c().get(WatchlistSkill)
    return (await skill.add(ticker, note or None)).as_dict()


async def list_watchlist() -> dict:
    """List the current watchlist tickers."""
    skill = await _c().get(WatchlistSkill)
    return (await skill.list()).as_dict()


async def set_price_alert(ticker: str, threshold: float, direction: str) -> dict:
    """Set a price alert. `direction` is "above" or "below". Records a local
    reminder only — no brokerage order is placed."""
    skill = await _c().get(AlertsSkill)
    return (await skill.set_alert(ticker, threshold, direction)).as_dict()


async def list_alerts() -> dict:
    """List configured price alerts."""
    skill = await _c().get(AlertsSkill)
    return (await skill.list()).as_dict()


async def log_trade(ticker: str, note: str, action: str = "", rationale: str = "") -> dict:
    """Log an entry to the trade journal (a note; `action` is an optional label
    like buy/sell). Records locally only — no trade is executed."""
    skill = await _c().get(JournalSkill)
    return (await skill.log(ticker, note, action or None, rationale or None)).as_dict()


async def list_journal(ticker: str = "") -> dict:
    """List trade-journal entries, optionally filtered by `ticker`."""
    skill = await _c().get(JournalSkill)
    return (await skill.list(ticker.strip().upper() or None)).as_dict()


SKILL_FUNCTIONS: list[Callable[..., Awaitable[dict]]] = [
    search_filings,
    search_news,
    get_quote,
    get_portfolio,
    add_to_watchlist,
    list_watchlist,
    set_price_alert,
    list_alerts,
    log_trade,
    list_journal,
]

TOOLS: dict[str, Callable[..., Awaitable[dict]]] = {f.__name__: f for f in SKILL_FUNCTIONS}


def build_adk_tools() -> list:
    """Wrap the skill functions as ADK FunctionTools."""
    from google.adk.tools import FunctionTool

    return [FunctionTool(func) for func in SKILL_FUNCTIONS]


def _type_name(annotation: Any) -> str:
    return {str: "string", float: "number", int: "integer", bool: "boolean"}.get(
        annotation, "string"
    )


def tool_schemas() -> list[dict]:
    """Lightweight schema list for the /tools API and docs."""
    schemas: list[dict] = []
    for func in SKILL_FUNCTIONS:
        sig = inspect.signature(func)
        params = {
            name: {
                "type": _type_name(p.annotation),
                "required": p.default is inspect.Parameter.empty,
                "default": None if p.default is inspect.Parameter.empty else p.default,
            }
            for name, p in sig.parameters.items()
        }
        schemas.append(
            {
                "name": func.__name__,
                "description": " ".join((func.__doc__ or "").split()),
                "parameters": params,
            }
        )
    return schemas


async def call_tool(name: str, arguments: dict[str, Any]) -> dict:
    func = TOOLS.get(name)
    if func is None:
        raise KeyError(name)
    return await func(**arguments)
