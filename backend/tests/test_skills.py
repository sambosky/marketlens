"""Skill behaviour with fakes (no DB / network)."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from infra.marketdata.types import Quote
from skills.market_data import MarketDataSkill
from skills.watchlist import WatchlistSkill


class FakeMarket:
    async def get_quote(self, ticker: str) -> Quote:
        return Quote(ticker=ticker.upper(), price=100.0, pe_ratio=25.0, as_of=datetime.now(timezone.utc))


async def test_market_data_skill_cites_live_source():
    result = (await MarketDataSkill(FakeMarket()).run("aapl")).as_dict()
    assert result["skill"] == "get_quote"
    assert result["data"]["price"] == 100.0
    assert result["citations"], "live quote must carry a citation"


class FakeWatchItem:
    def __init__(self, ticker: str, note: str | None) -> None:
        self.ticker = ticker.upper()
        self.note = note


class FakeWatchRepo:
    def __init__(self) -> None:
        self.added: list[str] = []

    async def add(self, *, ticker: str, note: str | None = None) -> FakeWatchItem:
        self.added.append(ticker.upper())
        return FakeWatchItem(ticker, note)


class NoopUoW:
    def __call__(self):
        @asynccontextmanager
        async def _cm():
            yield None

        return _cm()


async def test_watchlist_add_is_non_executing():
    repo = FakeWatchRepo()
    result = (await WatchlistSkill(repo, NoopUoW()).add("nvda")).as_dict()  # type: ignore[arg-type]
    assert repo.added == ["NVDA"]
    assert "no orders" in (result["note"] or "").lower()
