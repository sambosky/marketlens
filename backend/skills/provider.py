"""Dishka providers for retrievers and skills (the shared core layer)."""

from __future__ import annotations

from dishka import Provider, Scope, provide

from core.alerts.repo import AlertRepo
from core.filings.repo import FilingRepo
from core.journal.repo import JournalRepo
from core.news.repo import NewsRepo
from core.portfolio.repo import PositionRepo
from core.watchlist.repo import WatchlistRepo
from infra.db.uow import SQLAlchemyUnitOfWork
from infra.embedding.service import EmbeddingService
from infra.marketdata.types import MarketData
from retrieval.filings_retriever import FilingsRetriever
from retrieval.news_retriever import NewsRetriever
from skills.alerts import AlertsSkill
from skills.fundamentals import FundamentalsSkill
from skills.journal import JournalSkill
from skills.market_data import MarketDataSkill
from skills.news import NewsSkill
from skills.portfolio import PortfolioSkill
from skills.watchlist import WatchlistSkill


class RetrievalProvider(Provider):
    scope = Scope.APP

    @provide
    def filings_retriever(
        self, embedding: EmbeddingService, repo: FilingRepo
    ) -> FilingsRetriever:
        return FilingsRetriever(embedding, repo)

    @provide
    def news_retriever(self, embedding: EmbeddingService, repo: NewsRepo) -> NewsRetriever:
        return NewsRetriever(embedding, repo)


class SkillProvider(Provider):
    scope = Scope.APP

    @provide
    def fundamentals(self, retriever: FilingsRetriever) -> FundamentalsSkill:
        return FundamentalsSkill(retriever)

    @provide
    def news(self, retriever: NewsRetriever) -> NewsSkill:
        return NewsSkill(retriever)

    @provide
    def market(self, market: MarketData) -> MarketDataSkill:
        return MarketDataSkill(market)

    @provide
    def portfolio(self, positions: PositionRepo, market: MarketData) -> PortfolioSkill:
        return PortfolioSkill(positions, market)

    @provide
    def watchlist(self, repo: WatchlistRepo, uow: SQLAlchemyUnitOfWork) -> WatchlistSkill:
        return WatchlistSkill(repo, uow)

    @provide
    def alerts(self, repo: AlertRepo, uow: SQLAlchemyUnitOfWork) -> AlertsSkill:
        return AlertsSkill(repo, uow)

    @provide
    def journal(self, repo: JournalRepo, uow: SQLAlchemyUnitOfWork) -> JournalSkill:
        return JournalSkill(repo, uow)
