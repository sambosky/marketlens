from __future__ import annotations

from sqlalchemy import select

from core.models import Security
from core.sqlalchemy_repo import SQLAlchemyRepo


class SecurityRepo(SQLAlchemyRepo):
    async def get_by_ticker(self, ticker: str) -> Security | None:
        async with self._session() as s:
            result = await s.execute(select(Security).where(Security.ticker == ticker.upper()))
            return result.scalar_one_or_none()

    async def list_all(self) -> list[Security]:
        async with self._session() as s:
            result = await s.execute(select(Security).order_by(Security.ticker))
            return list(result.scalars().all())

    async def upsert(
        self,
        *,
        ticker: str,
        name: str,
        exchange: str | None = None,
        sector: str | None = None,
        cik: str | None = None,
    ) -> Security:
        async with self._session() as s:
            result = await s.execute(select(Security).where(Security.ticker == ticker.upper()))
            existing = result.scalar_one_or_none()
            if existing is not None:
                existing.name = name
                existing.exchange = exchange or existing.exchange
                existing.sector = sector or existing.sector
                existing.cik = cik or existing.cik
                await s.flush()
                return existing
            security = Security(
                ticker=ticker.upper(), name=name, exchange=exchange, sector=sector, cik=cik
            )
            s.add(security)
            await s.flush()
            return security
