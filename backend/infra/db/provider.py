"""Dishka provider for the database layer.

The engine is APP-scoped and yielded via an ``AsyncIterable`` so Dishka calls
``engine.dispose()`` on container shutdown — the canonical "DI owns the open
connection and cleans it up" pattern.
"""

from __future__ import annotations

from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from infra.db.uow import SQLAlchemyUnitOfWork
from settings import Settings


class DbProvider(Provider):
    scope = Scope.APP

    @provide
    async def engine(self, settings: Settings) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            settings.db.dsn,
            echo=settings.db.echo,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.max_overflow,
            pool_pre_ping=settings.db.pool_pre_ping,
        )
        try:
            yield engine
        finally:
            await engine.dispose()

    @provide
    def sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

    @provide
    def unit_of_work(
        self, sessionmaker: async_sessionmaker[AsyncSession]
    ) -> SQLAlchemyUnitOfWork:
        return SQLAlchemyUnitOfWork(sessionmaker)
