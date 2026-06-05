"""Minimal SEC EDGAR client (keyless).

Uses the shared ``httpx.AsyncClient`` (which carries the SEC-required
``User-Agent``). Throttled to stay well under SEC's ~10 req/s guidance.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx

_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
_ARCHIVE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{nodash}/{doc}"
_THROTTLE_SECONDS = 0.25


@dataclass
class FilingRef:
    form: str
    accession: str
    filed_at: datetime | None
    period: str | None
    primary_document: str
    title: str | None
    url: str


@dataclass
class CompanyInfo:
    cik: int
    ticker: str
    title: str


class EdgarClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client
        self._ticker_map: dict[str, CompanyInfo] | None = None

    async def _get(self, url: str) -> httpx.Response:
        await asyncio.sleep(_THROTTLE_SECONDS)
        response = await self._client.get(url)
        response.raise_for_status()
        return response

    async def _load_ticker_map(self) -> dict[str, CompanyInfo]:
        if self._ticker_map is None:
            data = (await self._get(_TICKERS_URL)).json()
            self._ticker_map = {
                row["ticker"].upper(): CompanyInfo(
                    cik=int(row["cik_str"]), ticker=row["ticker"].upper(), title=row["title"]
                )
                for row in data.values()
            }
        return self._ticker_map

    async def lookup_company(self, ticker: str) -> CompanyInfo | None:
        return (await self._load_ticker_map()).get(ticker.upper())

    async def recent_filings(
        self, cik: int, *, forms: tuple[str, ...], per_form: int
    ) -> list[FilingRef]:
        data = (await self._get(_SUBMISSIONS_URL.format(cik=cik))).json()
        recent = data.get("filings", {}).get("recent", {})
        accessions = recent.get("accessionNumber", [])
        form_list = recent.get("form", [])
        docs = recent.get("primaryDocument", [])
        filed = recent.get("filingDate", [])
        periods = recent.get("reportDate", [])
        descs = recent.get("primaryDocDescription", [])

        counts: dict[str, int] = {f: 0 for f in forms}
        out: list[FilingRef] = []
        for i in range(len(accessions)):
            form = form_list[i] if i < len(form_list) else ""
            if form not in counts or counts[form] >= per_form:
                continue
            if not (doc := docs[i] if i < len(docs) else ""):
                continue
            counts[form] += 1
            accession = accessions[i]
            out.append(
                FilingRef(
                    form=form,
                    accession=accession,
                    filed_at=_parse_date(filed[i] if i < len(filed) else None),
                    period=(periods[i] if i < len(periods) else None) or None,
                    primary_document=doc,
                    title=(descs[i] if i < len(descs) else None) or None,
                    url=_ARCHIVE_URL.format(cik=cik, nodash=accession.replace("-", ""), doc=doc),
                )
            )
            if all(counts[f] >= per_form for f in forms):
                break
        return out

    async def filing_text(self, ref: FilingRef) -> str:
        from ingestion.text import html_to_text

        body = (await self._get(ref.url)).text
        if ref.primary_document.lower().endswith((".htm", ".html")):
            return html_to_text(body)
        return body


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
