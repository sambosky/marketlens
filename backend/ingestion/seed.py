"""Seed a demo portfolio + watchlist (the read-only / action skills need state).

The positions here are fictional and exist only so "how's my position in X?"
has something to answer against.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal

from core.portfolio.repo import PositionRepo
from core.securities.repo import SecurityRepo
from core.watchlist.repo import WatchlistRepo
from infra.container import make_container
from settings import Settings, get_settings

log = logging.getLogger("ingestion.seed")

# (ticker, name, quantity, cost_basis, opened_at)
DEMO_POSITIONS = [
    ("NVDA", "NVIDIA Corporation", "50", "110.25", datetime(2024, 3, 14, tzinfo=timezone.utc)),
    ("AAPL", "Apple Inc.", "120", "171.40", datetime(2023, 11, 2, tzinfo=timezone.utc)),
    ("MSFT", "Microsoft Corporation", "40", "378.10", datetime(2024, 1, 22, tzinfo=timezone.utc)),
]
DEMO_WATCHLIST = ["TSLA", "AMZN"]


async def seed_demo(*, settings: Settings | None = None) -> None:
    settings = settings or get_settings()
    container = make_container(settings)
    try:
        positions = await container.get(PositionRepo)
        securities = await container.get(SecurityRepo)
        watchlist = await container.get(WatchlistRepo)

        existing = {p.ticker for p in await positions.list_all()}
        for ticker, name, qty, cost, opened in DEMO_POSITIONS:
            await securities.upsert(ticker=ticker, name=name)
            if ticker in existing:
                continue
            await positions.add(
                ticker=ticker,
                quantity=Decimal(qty),
                cost_basis=Decimal(cost),
                opened_at=opened,
            )
            log.info("Seeded position %s x%s @ %s", ticker, qty, cost)

        for ticker in DEMO_WATCHLIST:
            await watchlist.add(ticker=ticker, note="seed")
        log.info("Seed complete: %d positions, %d watchlist items.", len(DEMO_POSITIONS), len(DEMO_WATCHLIST))
    finally:
        await container.close()
