"""Ingest recent news (yfinance) → chunk → embed → ``news_chunk``.

Handles both the legacy flat yfinance news schema and the newer nested
``{"content": {...}}`` schema.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from core.news.repo import NewsRepo
from infra.container import make_container
from infra.embedding.service import EmbeddingService
from ingestion.text import chunk_text
from settings import Settings, get_settings

log = logging.getLogger("ingestion.news")

MAX_ARTICLES_PER_TICKER = 10


async def ingest_news(
    tickers: list[str] | None = None, *, settings: Settings | None = None
) -> None:
    settings = settings or get_settings()
    tickers = tickers or settings.ticker_universe
    container = make_container(settings)
    try:
        embedding = await container.get(EmbeddingService)
        news_repo = await container.get(NewsRepo)

        for ticker in tickers:
            raw = await asyncio.to_thread(_fetch_news, ticker)
            for item in raw[:MAX_ARTICLES_PER_TICKER]:
                parsed = _parse_item(item)
                if parsed is None:
                    continue
                if await news_repo.url_exists(parsed["url"]):
                    continue
                body = f"{parsed['headline']}\n\n{parsed['summary'] or ''}".strip()
                chunks = chunk_text(body)
                if not chunks:
                    continue
                embeddings = await embedding.embed_texts(chunks)
                await news_repo.create(
                    ticker=ticker,
                    headline=parsed["headline"],
                    url=parsed["url"],
                    publisher=parsed["publisher"],
                    published_at=parsed["published_at"],
                    summary=parsed["summary"],
                    chunks=list(enumerate(chunks)),
                    embeddings=embeddings,
                )
                log.info("Ingested news for %s: %s", ticker, parsed["headline"][:70])

        total = await news_repo.count()
        log.info("News ingest complete. %d articles in DB.", total)
    finally:
        await container.close()


def _fetch_news(ticker: str) -> list[dict]:
    import yfinance as yf

    try:
        return list(yf.Ticker(ticker).news or [])
    except Exception as exc:  # noqa: BLE001 - best effort
        log.warning("yfinance news failed for %s: %s", ticker, exc)
        return []


def _parse_item(item: dict) -> dict | None:
    content = item.get("content")
    if isinstance(content, dict):  # newer schema
        url = (content.get("canonicalUrl") or {}).get("url") or (
            content.get("clickThroughUrl") or {}
        ).get("url")
        return _maybe(
            headline=content.get("title"),
            url=url,
            publisher=(content.get("provider") or {}).get("displayName"),
            summary=content.get("summary") or content.get("description"),
            published_at=_parse_iso(content.get("pubDate")),
        )
    return _maybe(  # legacy flat schema
        headline=item.get("title"),
        url=item.get("link"),
        publisher=item.get("publisher"),
        summary=item.get("summary"),
        published_at=_parse_epoch(item.get("providerPublishTime")),
    )


def _maybe(*, headline, url, publisher, summary, published_at) -> dict | None:
    if not headline or not url:
        return None
    return {
        "headline": headline,
        "url": url,
        "publisher": publisher,
        "summary": summary,
        "published_at": published_at,
    }


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_epoch(value: object) -> datetime | None:
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
