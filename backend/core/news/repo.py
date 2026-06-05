from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select

from core.models import NewsArticle, NewsChunk
from core.sqlalchemy_repo import SQLAlchemyRepo


@dataclass
class NewsChunkHit:
    chunk: NewsChunk
    article: NewsArticle
    distance: float

    @property
    def similarity(self) -> float:
        return 1.0 - self.distance


class NewsRepo(SQLAlchemyRepo):
    async def url_exists(self, url: str) -> bool:
        async with self._session() as s:
            result = await s.execute(select(NewsArticle.id).where(NewsArticle.url == url))
            return result.scalar_one_or_none() is not None

    async def count(self) -> int:
        async with self._session() as s:
            return int((await s.execute(select(func.count(NewsArticle.id)))).scalar_one())

    async def create(
        self,
        *,
        ticker: str,
        headline: str,
        url: str,
        publisher: str | None,
        published_at: datetime | None,
        summary: str | None,
        chunks: list[tuple[int, str]],  # (ordinal, text)
        embeddings: list[list[float]],
    ) -> NewsArticle:
        async with self._session() as s:
            article = NewsArticle(
                ticker=ticker.upper(),
                headline=headline,
                url=url,
                publisher=publisher,
                published_at=published_at,
                summary=summary,
            )
            s.add(article)
            await s.flush()
            for (ordinal, text), embedding in zip(chunks, embeddings, strict=True):
                s.add(
                    NewsChunk(
                        news_article_id=article.id,
                        ordinal=ordinal,
                        text=text,
                        embedding=embedding,
                    )
                )
            await s.flush()
            return article

    async def search_similar(
        self, embedding: list[float], *, limit: int = 8, tickers: list[str] | None = None
    ) -> list[NewsChunkHit]:
        distance = NewsChunk.embedding.cosine_distance(embedding).label("distance")
        stmt = (
            select(NewsChunk, NewsArticle, distance)
            .join(NewsArticle, NewsChunk.news_article_id == NewsArticle.id)
            .order_by(distance)
            .limit(limit)
        )
        if tickers:
            stmt = stmt.where(NewsArticle.ticker.in_([t.upper() for t in tickers]))
        async with self._session() as s:
            rows = (await s.execute(stmt)).all()
        return [NewsChunkHit(chunk=c, article=a, distance=float(d)) for c, a, d in rows]
