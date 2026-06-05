from __future__ import annotations

from sqlalchemy import delete, select

from core.models import WatchlistItem
from core.sqlalchemy_repo import SQLAlchemyRepo


class WatchlistRepo(SQLAlchemyRepo):
    async def list_all(self) -> list[WatchlistItem]:
        async with self._session() as s:
            result = await s.execute(select(WatchlistItem).order_by(WatchlistItem.ticker))
            return list(result.scalars().all())

    async def add(self, *, ticker: str, note: str | None = None) -> WatchlistItem:
        """Idempotent add — returns the existing item if already watched."""
        async with self._session() as s:
            result = await s.execute(
                select(WatchlistItem).where(WatchlistItem.ticker == ticker.upper())
            )
            existing = result.scalar_one_or_none()
            if existing is not None:
                if note:
                    existing.note = note
                await s.flush()
                return existing
            item = WatchlistItem(ticker=ticker.upper(), note=note)
            s.add(item)
            await s.flush()
            return item

    async def remove(self, ticker: str) -> bool:
        async with self._session() as s:
            result = await s.execute(
                delete(WatchlistItem).where(WatchlistItem.ticker == ticker.upper())
            )
            return result.rowcount > 0
