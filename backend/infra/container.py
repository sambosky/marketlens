"""Dishka container assembly.

One async container wires every provider. It is created once at app startup
(see ``api/main.py``) and closed on shutdown, which disposes the engine, closes
the HTTP client, etc.
"""

from __future__ import annotations

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide

from core.provider import RepositoryProvider
from infra.db.provider import DbProvider
from infra.embedding.provider import EmbeddingProvider
from infra.http.provider import HttpClientProvider
from infra.llm.provider import LLMProvider
from infra.marketdata.provider import MarketDataProvider
from settings import Settings, get_settings


class ConfigProvider(Provider):
    """Exposes the app Settings instance to the container."""

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return self._settings


def make_container(settings: Settings | None = None) -> AsyncContainer:
    settings = settings or get_settings()
    return make_async_container(
        ConfigProvider(settings),
        DbProvider(),
        EmbeddingProvider(),
        LLMProvider(),
        HttpClientProvider(),
        MarketDataProvider(),
        RepositoryProvider(),
    )
