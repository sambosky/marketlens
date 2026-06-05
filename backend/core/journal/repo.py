from __future__ import annotations

from sqlalchemy import select

from core.models import JournalEntry
from core.sqlalchemy_repo import SQLAlchemyRepo


class JournalRepo(SQLAlchemyRepo):
    async def add(
        self,
        *,
        ticker: str,
        note: str,
        action: str | None = None,
        rationale: str | None = None,
    ) -> JournalEntry:
        async with self._session() as s:
            entry = JournalEntry(
                ticker=ticker.upper(), note=note, action=action, rationale=rationale
            )
            s.add(entry)
            await s.flush()
            return entry

    async def list_all(self, limit: int = 100) -> list[JournalEntry]:
        async with self._session() as s:
            result = await s.execute(
                select(JournalEntry).order_by(JournalEntry.created_at.desc()).limit(limit)
            )
            return list(result.scalars().all())

    async def list_by_ticker(self, ticker: str, limit: int = 100) -> list[JournalEntry]:
        async with self._session() as s:
            result = await s.execute(
                select(JournalEntry)
                .where(JournalEntry.ticker == ticker.upper())
                .order_by(JournalEntry.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
