from __future__ import annotations

from core.news.repo import NewsRepo
from infra.embedding.service import EmbeddingService
from retrieval.interfaces import Citation, Evidence


class NewsRetriever:
    """Semantic retrieval over news chunks (pgvector cosine)."""

    def __init__(self, embedding: EmbeddingService, repo: NewsRepo) -> None:
        self._embedding = embedding
        self._repo = repo

    async def retrieve(
        self, query: str, *, tickers: list[str] | None = None, limit: int = 6
    ) -> list[Evidence]:
        vector = await self._embedding.embed_text(query)
        hits = await self._repo.search_similar(vector, limit=limit, tickers=tickers)
        evidence: list[Evidence] = []
        for hit in hits:
            article = hit.article
            label = article.publisher or "news"
            if article.published_at is not None:
                label += f" ({article.published_at.date().isoformat()})"
            evidence.append(
                Evidence(
                    text=f"{article.headline}. {hit.chunk.text}",
                    citation=Citation(source=label, url=article.url, detail=article.headline),
                    score=round(hit.similarity, 4),
                )
            )
        return evidence
