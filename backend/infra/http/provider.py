"""Dishka provider for a shared async HTTP client.

One ``httpx.AsyncClient`` is shared app-wide (used by SEC EDGAR ingestion and
any keyless HTTP fetching) and closed on shutdown — another "DI owns the open
connection" example. SEC requires a descriptive ``User-Agent``, set here from
settings.
"""

from __future__ import annotations

from collections.abc import AsyncIterable

import httpx
from dishka import Provider, Scope, provide

from settings import Settings


class HttpClientProvider(Provider):
    scope = Scope.APP

    @provide
    async def client(self, settings: Settings) -> AsyncIterable[httpx.AsyncClient]:
        client = httpx.AsyncClient(
            headers={"User-Agent": settings.sec_user_agent},
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )
        try:
            yield client
        finally:
            await client.aclose()
