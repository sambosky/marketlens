from __future__ import annotations

from decimal import Decimal, InvalidOperation

from core.alerts.repo import AlertRepo
from infra.db.uow import SQLAlchemyUnitOfWork
from skills.types import SkillResult

NAME = "alerts"
_DISCLAIMER = "This is a local reminder, not a brokerage order."


class AlertsSkill:
    """Non-executing action: set/list price alerts."""

    def __init__(self, repo: AlertRepo, uow: SQLAlchemyUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    async def set_alert(self, ticker: str, threshold: float, direction: str) -> SkillResult:
        direction = direction.strip().lower()
        if direction not in ("above", "below"):
            return SkillResult(skill="set_price_alert", note="direction must be 'above' or 'below'.")
        try:
            value = Decimal(str(threshold))
        except (InvalidOperation, ValueError):
            return SkillResult(skill="set_price_alert", note="threshold must be a number.")

        async with self._uow():
            alert = await self._repo.add(ticker=ticker, threshold=value, direction=direction)
        return SkillResult(
            skill="set_price_alert",
            summary=f"Alert set: notify when {alert.ticker} goes {direction} {threshold}.",
            data={
                "id": alert.id,
                "ticker": alert.ticker,
                "threshold": float(alert.threshold),
                "direction": alert.direction,
                "status": alert.status,
            },
            note=_DISCLAIMER,
        )

    async def list(self) -> SkillResult:
        alerts = await self._repo.list_all()
        return SkillResult(
            skill="list_alerts",
            data={
                "alerts": [
                    {
                        "id": a.id,
                        "ticker": a.ticker,
                        "threshold": float(a.threshold),
                        "direction": a.direction,
                        "status": a.status,
                    }
                    for a in alerts
                ]
            },
        )
