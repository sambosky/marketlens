from __future__ import annotations

from core.journal.repo import JournalRepo
from infra.db.uow import SQLAlchemyUnitOfWork
from skills.types import SkillResult

NAME = "journal"
_DISCLAIMER = "Logged to your local trade journal — no trade was executed."


class JournalSkill:
    """Non-executing action: log/list trade-journal entries."""

    def __init__(self, repo: JournalRepo, uow: SQLAlchemyUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    async def log(
        self,
        ticker: str,
        note: str,
        action: str | None = None,
        rationale: str | None = None,
    ) -> SkillResult:
        async with self._uow():
            entry = await self._repo.add(
                ticker=ticker, note=note, action=action, rationale=rationale
            )
        return SkillResult(
            skill="log_trade",
            summary=f"Journaled an entry for {entry.ticker}.",
            data={"id": entry.id, "ticker": entry.ticker, "action": entry.action},
            note=_DISCLAIMER,
        )

    async def list(self, ticker: str | None = None) -> SkillResult:
        entries = (
            await self._repo.list_by_ticker(ticker) if ticker else await self._repo.list_all()
        )
        return SkillResult(
            skill="list_journal",
            data={
                "entries": [
                    {
                        "id": e.id,
                        "ticker": e.ticker,
                        "action": e.action,
                        "note": e.note,
                        "rationale": e.rationale,
                        "created_at": e.created_at.isoformat() if e.created_at else None,
                    }
                    for e in entries
                ]
            },
        )
