from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from core.models import Position
from core.sqlalchemy_repo import SQLAlchemyRepo


class PositionRepo(SQLAlchemyRepo):
    async def list_all(self) -> list[Position]:
        async with self._session() as s:
            result = await s.execute(select(Position).order_by(Position.ticker))
            return list(result.scalars().all())

    async def list_by_ticker(self, ticker: str) -> list[Position]:
        async with self._session() as s:
            result = await s.execute(select(Position).where(Position.ticker == ticker.upper()))
            return list(result.scalars().all())

    async def add(
        self,
        *,
        ticker: str,
        quantity: Decimal,
        cost_basis: Decimal,
        opened_at: datetime | None = None,
    ) -> Position:
        async with self._session() as s:
            position = Position(
                ticker=ticker.upper(),
                quantity=quantity,
                cost_basis=cost_basis,
                opened_at=opened_at,
            )
            s.add(position)
            await s.flush()
            return position
