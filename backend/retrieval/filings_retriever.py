from __future__ import annotations

from core.filings.repo import FilingRepo
from infra.embedding.service import EmbeddingService
from retrieval.interfaces import Citation, Evidence


class FilingsRetriever:
    """Semantic retrieval over SEC filing chunks (pgvector cosine)."""

    def __init__(self, embedding: EmbeddingService, repo: FilingRepo) -> None:
        self._embedding = embedding
        self._repo = repo

    async def retrieve(
        self, query: str, *, tickers: list[str] | None = None, limit: int = 6
    ) -> list[Evidence]:
        vector = await self._embedding.embed_text(query)
        hits = await self._repo.search_similar(vector, limit=limit, tickers=tickers)
        evidence: list[Evidence] = []
        for hit in hits:
            filing = hit.filing
            label = f"{filing.ticker} {filing.form_type}"
            if filing.filed_at is not None:
                label += f" (filed {filing.filed_at.date().isoformat()})"
            evidence.append(
                Evidence(
                    text=hit.chunk.text,
                    citation=Citation(source=label, url=filing.url, detail=filing.accession),
                    score=round(hit.similarity, 4),
                )
            )
        return evidence
