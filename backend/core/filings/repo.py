from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select

from core.models import Filing, FilingChunk
from core.sqlalchemy_repo import SQLAlchemyRepo


@dataclass
class FilingChunkHit:
    chunk: FilingChunk
    filing: Filing
    distance: float

    @property
    def similarity(self) -> float:
        return 1.0 - self.distance


class FilingRepo(SQLAlchemyRepo):
    async def exists(self, accession: str) -> bool:
        async with self._session() as s:
            result = await s.execute(select(Filing.id).where(Filing.accession == accession))
            return result.scalar_one_or_none() is not None

    async def count(self) -> int:
        async with self._session() as s:
            return int((await s.execute(select(func.count(Filing.id)))).scalar_one())

    async def create(
        self,
        *,
        cik: str,
        ticker: str,
        form_type: str,
        accession: str,
        url: str,
        period: str | None,
        filed_at: datetime | None,
        title: str | None,
        chunks: list[tuple[int, str | None, str]],  # (ordinal, section, text)
        embeddings: list[list[float]],
    ) -> Filing:
        async with self._session() as s:
            filing = Filing(
                cik=cik,
                ticker=ticker.upper(),
                form_type=form_type,
                accession=accession,
                url=url,
                period=period,
                filed_at=filed_at,
                title=title,
            )
            s.add(filing)
            await s.flush()
            for (ordinal, section, text), embedding in zip(chunks, embeddings, strict=True):
                s.add(
                    FilingChunk(
                        filing_id=filing.id,
                        ordinal=ordinal,
                        section=section,
                        text=text,
                        embedding=embedding,
                    )
                )
            await s.flush()
            return filing

    async def search_similar(
        self, embedding: list[float], *, limit: int = 8, tickers: list[str] | None = None
    ) -> list[FilingChunkHit]:
        distance = FilingChunk.embedding.cosine_distance(embedding).label("distance")
        stmt = (
            select(FilingChunk, Filing, distance)
            .join(Filing, FilingChunk.filing_id == Filing.id)
            .order_by(distance)
            .limit(limit)
        )
        if tickers:
            stmt = stmt.where(Filing.ticker.in_([t.upper() for t in tickers]))
        async with self._session() as s:
            rows = (await s.execute(stmt)).all()
        return [FilingChunkHit(chunk=c, filing=f, distance=float(d)) for c, f, d in rows]
