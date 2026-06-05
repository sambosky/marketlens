"""initial schema (pgvector + all tables)

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-05

The schema is created from the SQLAlchemy metadata (the models are the single
source of truth); this migration adds the ``vector`` extension first and the
HNSW vector indexes afterwards.
"""

from __future__ import annotations

from alembic import op

from core.models import Base

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

FILING_INDEX = (
    "CREATE INDEX IF NOT EXISTS ix_filing_chunk_embedding "
    "ON filing_chunk USING hnsw (embedding vector_cosine_ops)"
)
NEWS_INDEX = (
    "CREATE INDEX IF NOT EXISTS ix_news_chunk_embedding "
    "ON news_chunk USING hnsw (embedding vector_cosine_ops)"
)


def upgrade() -> None:
    bind = op.get_bind()
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind)
    op.execute(FILING_INDEX)
    op.execute(NEWS_INDEX)


def downgrade() -> None:
    bind = op.get_bind()
    op.execute("DROP INDEX IF EXISTS ix_news_chunk_embedding")
    op.execute("DROP INDEX IF EXISTS ix_filing_chunk_embedding")
    Base.metadata.drop_all(bind)
