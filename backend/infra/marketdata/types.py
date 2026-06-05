"""Market-data types and the provider protocol."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel


class Quote(BaseModel):
    ticker: str
    price: float | None = None
    currency: str | None = None
    previous_close: float | None = None
    change: float | None = None
    change_percent: float | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    day_high: float | None = None
    day_low: float | None = None
    as_of: datetime
    # Citation string carried through to the synthesis layer.
    source: str = "live market data (yfinance)"


class MarketData(Protocol):
    """A live market-data source. Implementations must be safe to share app-wide."""

    async def get_quote(self, ticker: str) -> Quote | None: ...
