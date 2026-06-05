"""FastAPI application factory.

Phase 1 wires the Dishka container into FastAPI (``setup_dishka``) and exposes a
health check. The lifespan closes the container on shutdown, disposing the
engine and the shared HTTP client. Domain routes are added in P4.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infra.container import make_container
from settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    container = make_container(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await app.state.dishka_container.close()

    app = FastAPI(title="MarketLens API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "llm_provider": settings.llm.provider}

    setup_dishka(container, app)
    return app


app = create_app()
