from __future__ import annotations

from core.portfolio.repo import PositionRepo
from infra.marketdata.types import MarketData
from retrieval.interfaces import Citation
from skills.types import SkillResult

NAME = "get_portfolio"


class PortfolioSkill:
    """Read-only view of the (seeded, demo) portfolio, marked to live prices."""

    def __init__(self, positions: PositionRepo, market: MarketData) -> None:
        self._positions = positions
        self._market = market

    async def run(self, ticker: str | None = None) -> SkillResult:
        rows = (
            await self._positions.list_by_ticker(ticker)
            if ticker
            else await self._positions.list_all()
        )
        if not rows:
            target = ticker.upper() if ticker else "your portfolio"
            return SkillResult(skill=NAME, note=f"No positions found for {target}.")

        used_live = False
        items: list[dict] = []
        for p in rows:
            qty = float(p.quantity)
            cost = float(p.cost_basis)
            quote = await self._market.get_quote(p.ticker)
            price = quote.price if quote else None
            if price is not None:
                used_live = True
            items.append(
                {
                    "ticker": p.ticker,
                    "quantity": qty,
                    "cost_basis": cost,
                    "price": price,
                    "market_value": round(price * qty, 2) if price is not None else None,
                    "unrealized_pnl": round((price - cost) * qty, 2) if price is not None else None,
                    "unrealized_pnl_pct": round((price / cost - 1) * 100, 2)
                    if price is not None and cost
                    else None,
                }
            )

        citations = [Citation(source="your portfolio (local demo data)")]
        if used_live:
            citations.append(Citation(source="live market data (yfinance)"))
        return SkillResult(skill=NAME, data={"positions": items}, citations=citations)
