"""Dishka provider for the repositories.

Repos are APP-scoped: they hold only the (app-scoped) sessionmaker and open a
fresh session per call — or join the active Unit-of-Work transaction. This keeps
them cheap to share and safe to use from both HTTP routes and the agent tools.
"""

from __future__ import annotations

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.alerts.repo import AlertRepo
from core.journal.repo import JournalRepo
from core.portfolio.repo import PositionRepo
from core.securities.repo import SecurityRepo
from core.watchlist.repo import WatchlistRepo

SessionMaker = async_sessionmaker[AsyncSession]


class RepositoryProvider(Provider):
    scope = Scope.APP

    @provide
    def securities(self, sessionmaker: SessionMaker) -> SecurityRepo:
        return SecurityRepo(sessionmaker)

    @provide
    def positions(self, sessionmaker: SessionMaker) -> PositionRepo:
        return PositionRepo(sessionmaker)

    @provide
    def watchlist(self, sessionmaker: SessionMaker) -> WatchlistRepo:
        return WatchlistRepo(sessionmaker)

    @provide
    def alerts(self, sessionmaker: SessionMaker) -> AlertRepo:
        return AlertRepo(sessionmaker)

    @provide
    def journal(self, sessionmaker: SessionMaker) -> JournalRepo:
        return JournalRepo(sessionmaker)
