"""Unit of Work with a ``ContextVar``-shared session.

When a request enters the UoW, every repository call made inside it reuses the
same `AsyncSession` and participates in one transaction (commit on success,
rollback on error). Outside a UoW, repositories open their own short-lived
session per call (see ``core.sqlalchemy_repo``).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

_current_session: ContextVar[AsyncSession | None] = ContextVar("current_session", default=None)


def get_current_session() -> AsyncSession | None:
    """Return the session for the active UoW transaction, if any."""
    return _current_session.get()


class SQLAlchemyUnitOfWork:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker

    @asynccontextmanager
    async def __call__(self) -> AsyncIterator[AsyncSession]:
        existing = _current_session.get()
        if existing is not None:
            # Already inside a UoW — join it; the outermost call owns commit/rollback.
            yield existing
            return

        async with self._sessionmaker() as session:
            token = _current_session.set(session)
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                _current_session.reset(token)
