from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from core.models import PriceAlert
from core.sqlalchemy_repo import SQLAlchemyRepo


class AlertRepo(SQLAlchemyRepo):
    async def add(self, *, ticker: str, threshold: Decimal, direction: str) -> PriceAlert:
        if direction not in ("above", "below"):
            raise ValueError("direction must be 'above' or 'below'")
        async with self._session() as s:
            alert = PriceAlert(
                ticker=ticker.upper(), threshold=threshold, direction=direction, status="active"
            )
            s.add(alert)
            await s.flush()
            return alert

    async def list_all(self) -> list[PriceAlert]:
        async with self._session() as s:
            result = await s.execute(select(PriceAlert).order_by(PriceAlert.created_at.desc()))
            return list(result.scalars().all())

    async def list_active(self) -> list[PriceAlert]:
        async with self._session() as s:
            result = await s.execute(
                select(PriceAlert).where(PriceAlert.status == "active").order_by(PriceAlert.ticker)
            )
            return list(result.scalars().all())

    async def set_status(self, alert_id: int, status: str) -> PriceAlert | None:
        async with self._session() as s:
            alert = await s.get(PriceAlert, alert_id)
            if alert is None:
                return None
            alert.status = status
            await s.flush()
            return alert
