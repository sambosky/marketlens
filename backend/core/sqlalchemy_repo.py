"""Base repository: UoW-aware session management.

Each repo is constructed with an app-scoped ``async_sessionmaker``. On every
operation it calls ``_session()`` which:

* reuses the active Unit-of-Work session if one is set (so the call joins the
  surrounding transaction), or
* opens a fresh session and commits it when no UoW is active.

This mirrors the pattern used in production codebases and keeps repos usable
both standalone and inside a transaction without threading a session around.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infra.db.uow import get_current_session


class SQLAlchemyRepo:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker

    @asynccontextmanager
    async def _session(self) -> AsyncIterator[AsyncSession]:
        existing = get_current_session()
        if existing is not None:
            # Inside a UoW: reuse its session; commit is owned by the UoW.
            yield existing
        else:
            async with self._sessionmaker() as session:
                yield session
                await session.commit()
