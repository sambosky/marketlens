"""Dishka provider for the embedding service (APP scope — model loaded once)."""

from __future__ import annotations

from dishka import Provider, Scope, provide

from infra.embedding.service import EmbeddingService, FastEmbedEmbeddingService
from settings import Settings


class EmbeddingProvider(Provider):
    scope = Scope.APP

    @provide
    def embedding(self, settings: Settings) -> EmbeddingService:
        return FastEmbedEmbeddingService(settings.embedding.model, settings.embedding.dim)
