"""SQLAlchemy ORM models (SQLAlchemy 2.0 typed mappings).

The RAG corpus tables (`filing_chunk`, `news_chunk`) carry a pgvector
``embedding`` column; everything else is plain relational state for the
portfolio / watchlist / alerts / journal skills.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Dimensionality of BAAI/bge-small-en-v1.5 (the default fastembed model).
EMBEDDING_DIM = 384


class Base(DeclarativeBase):
    """Declarative base for all MarketLens ORM models."""


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ── Reference data ────────────────────────────────────────────────────────────
class Security(TimestampMixin, Base):
    __tablename__ = "security"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(256))
    exchange: Mapped[str | None] = mapped_column(String(32), default=None)
    sector: Mapped[str | None] = mapped_column(String(128), default=None)
    cik: Mapped[str | None] = mapped_column(String(16), default=None, index=True)


# ── RAG corpus: SEC filings ───────────────────────────────────────────────────
class Filing(TimestampMixin, Base):
    __tablename__ = "filing"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cik: Mapped[str] = mapped_column(String(16), index=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    form_type: Mapped[str] = mapped_column(String(16))
    period: Mapped[str | None] = mapped_column(String(32), default=None)
    filed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    accession: Mapped[str] = mapped_column(String(32), unique=True)
    url: Mapped[str] = mapped_column(String(512))
    title: Mapped[str | None] = mapped_column(String(512), default=None)

    chunks: Mapped[list[FilingChunk]] = relationship(
        back_populates="filing", cascade="all, delete-orphan"
    )


class FilingChunk(Base):
    __tablename__ = "filing_chunk"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    filing_id: Mapped[int] = mapped_column(
        ForeignKey("filing.id", ondelete="CASCADE"), index=True
    )
    section: Mapped[str | None] = mapped_column(String(128), default=None)
    ordinal: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))

    filing: Mapped[Filing] = relationship(back_populates="chunks")


# ── RAG corpus: news ──────────────────────────────────────────────────────────
class NewsArticle(TimestampMixin, Base):
    __tablename__ = "news_article"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    headline: Mapped[str] = mapped_column(String(512))
    publisher: Mapped[str | None] = mapped_column(String(128), default=None)
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    summary: Mapped[str | None] = mapped_column(Text, default=None)

    chunks: Mapped[list[NewsChunk]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )


class NewsChunk(Base):
    __tablename__ = "news_chunk"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    news_article_id: Mapped[int] = mapped_column(
        ForeignKey("news_article.id", ondelete="CASCADE"), index=True
    )
    ordinal: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIM))

    article: Mapped[NewsArticle] = relationship(back_populates="chunks")


# ── Portfolio (read-only skill, seeded) ───────────────────────────────────────
class Position(TimestampMixin, Base):
    __tablename__ = "position"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    cost_basis: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)


# ── Action skills (non-executing) ─────────────────────────────────────────────
class WatchlistItem(TimestampMixin, Base):
    __tablename__ = "watchlist_item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    note: Mapped[str | None] = mapped_column(String(512), default=None)


class PriceAlert(TimestampMixin, Base):
    __tablename__ = "price_alert"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    threshold: Mapped[Decimal] = mapped_column(Numeric(20, 6))
    direction: Mapped[str] = mapped_column(String(8))  # "above" | "below"
    status: Mapped[str] = mapped_column(String(16), default="active")  # active|triggered|cancelled


class JournalEntry(TimestampMixin, Base):
    __tablename__ = "journal_entry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), index=True)
    action: Mapped[str | None] = mapped_column(String(32), default=None)  # note|buy|sell (label only)
    note: Mapped[str] = mapped_column(Text)
    rationale: Mapped[str | None] = mapped_column(Text, default=None)


# ── Live-quote cache (resilience for the live source) ─────────────────────────
class QuoteCache(Base):
    __tablename__ = "quote_cache"

    ticker: Mapped[str] = mapped_column(String(16), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSONB)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
