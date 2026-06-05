"""Retrieval contracts and cited-evidence types."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel


class Citation(BaseModel):
    """A source reference attached to every fact the system surfaces."""

    source: str  # human-readable label, e.g. "NVDA 10-Q (filed 2024-08-28)"
    url: str | None = None
    detail: str | None = None  # e.g. accession number, section, timestamp


class Evidence(BaseModel):
    text: str
    citation: Citation
    score: float | None = None


class Retriever(Protocol):
    async def retrieve(
        self, query: str, *, tickers: list[str] | None = None, limit: int = 6
    ) -> list[Evidence]: ...
