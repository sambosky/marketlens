"""Ingestion CLI entrypoint.

Usage::

    python -m ingestion.cli all       # seed + filings + news
    python -m ingestion.cli filings --per-form 2
    python -m ingestion.cli news
    python -m ingestion.cli seed
"""

from __future__ import annotations

import argparse
import asyncio
import logging

from ingestion.ingest_filings import ingest_filings
from ingestion.ingest_news import ingest_news
from ingestion.seed import seed_demo


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="MarketLens ingestion")
    parser.add_argument("command", choices=["all", "filings", "news", "seed"])
    parser.add_argument("--per-form", type=int, default=1, help="filings per form type per ticker")
    args = parser.parse_args()
    asyncio.run(_run(args))


async def _run(args: argparse.Namespace) -> None:
    if args.command in ("all", "seed"):
        await seed_demo()
    if args.command in ("all", "filings"):
        await ingest_filings(per_form=args.per_form)
    if args.command in ("all", "news"):
        await ingest_news()


if __name__ == "__main__":
    main()
