from __future__ import annotations

from core.watchlist.repo import WatchlistRepo
from infra.db.uow import SQLAlchemyUnitOfWork
from skills.types import SkillResult

NAME = "watchlist"
_DISCLAIMER = "Recorded locally — MarketLens places no orders."


class WatchlistSkill:
    """Non-executing action: add/list/remove watchlist tickers."""

    def __init__(self, repo: WatchlistRepo, uow: SQLAlchemyUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    async def add(self, ticker: str, note: str | None = None) -> SkillResult:
        async with self._uow():
            item = await self._repo.add(ticker=ticker, note=note)
        return SkillResult(
            skill="add_to_watchlist",
            summary=f"Added {item.ticker} to your watchlist.",
            data={"ticker": item.ticker, "note": item.note},
            note=_DISCLAIMER,
        )

    async def remove(self, ticker: str) -> SkillResult:
        async with self._uow():
            removed = await self._repo.remove(ticker)
        return SkillResult(
            skill="remove_from_watchlist",
            summary=(
                f"Removed {ticker.upper()} from your watchlist."
                if removed
                else f"{ticker.upper()} was not on your watchlist."
            ),
            data={"ticker": ticker.upper(), "removed": removed},
        )

    async def list(self) -> SkillResult:
        items = await self._repo.list_all()
        return SkillResult(
            skill="list_watchlist",
            data={"watchlist": [{"ticker": i.ticker, "note": i.note} for i in items]},
        )
