"""SQLAlchemy ORM models.

NOTE (P0): only the declarative ``Base`` lives here for now so the Alembic
environment imports cleanly. The full schema (securities, filings, filing
chunks with pgvector embeddings, news, portfolio, watchlist, alerts, journal)
is added in P1.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all MarketLens ORM models."""
