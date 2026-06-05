"""Ingest recent SEC filings → chunk → embed → ``filing_chunk``."""

from __future__ import annotations

import logging

import httpx

from core.filings.repo import FilingRepo
from core.securities.repo import SecurityRepo
from infra.container import make_container
from infra.embedding.service import EmbeddingService
from ingestion.edgar import EdgarClient
from ingestion.text import chunk_text
from settings import Settings, get_settings

log = logging.getLogger("ingestion.filings")

FORMS = ("10-K", "10-Q", "8-K")
MAX_CHUNKS_PER_FILING = 40


async def ingest_filings(
    tickers: list[str] | None = None,
    *,
    per_form: int = 1,
    settings: Settings | None = None,
) -> None:
    settings = settings or get_settings()
    tickers = tickers or settings.ticker_universe
    container = make_container(settings)
    try:
        embedding = await container.get(EmbeddingService)
        http = await container.get(httpx.AsyncClient)
        filing_repo = await container.get(FilingRepo)
        security_repo = await container.get(SecurityRepo)
        edgar = EdgarClient(http)

        for ticker in tickers:
            company = await edgar.lookup_company(ticker)
            if company is None:
                log.warning("No CIK found for %s — skipping", ticker)
                continue
            await security_repo.upsert(ticker=ticker, name=company.title, cik=str(company.cik))

            refs = await edgar.recent_filings(company.cik, forms=FORMS, per_form=per_form)
            for ref in refs:
                if await filing_repo.exists(ref.accession):
                    log.info("Already ingested %s %s", ticker, ref.accession)
                    continue
                try:
                    text = await edgar.filing_text(ref)
                except (httpx.HTTPError, Exception) as exc:  # noqa: BLE001 - best-effort ingest
                    log.warning("Fetch failed %s %s: %s", ticker, ref.accession, exc)
                    continue

                chunks = chunk_text(text)[:MAX_CHUNKS_PER_FILING]
                if not chunks:
                    continue
                embeddings = await embedding.embed_texts(chunks)
                await filing_repo.create(
                    cik=str(company.cik),
                    ticker=ticker,
                    form_type=ref.form,
                    accession=ref.accession,
                    url=ref.url,
                    period=ref.period,
                    filed_at=ref.filed_at,
                    title=ref.title,
                    chunks=[(i, ref.form, c) for i, c in enumerate(chunks)],
                    embeddings=embeddings,
                )
                log.info("Ingested %s %s — %d chunks", ticker, ref.form, len(chunks))

        total = await filing_repo.count()
        log.info("Filings ingest complete. %d filings in DB.", total)
    finally:
        await container.close()
