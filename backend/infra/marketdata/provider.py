"""Dishka provider for the market-data source."""

from __future__ import annotations

from dishka import Provider, Scope, provide

from infra.marketdata.types import MarketData
from infra.marketdata.yfinance_provider import YFinanceMarketData


class MarketDataProvider(Provider):
    scope = Scope.APP

    @provide
    def market_data(self) -> MarketData:
        return YFinanceMarketData()
