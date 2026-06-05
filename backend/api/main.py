"""FastAPI application factory.

Wires the Dishka container into FastAPI, builds the ADK agent at startup (binding
the tool container so the skill tools can resolve their dependencies), mounts the
routes, and closes the container on shutdown.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.adk.models.lite_llm import LiteLlm

from agents.runner import MarketLensAgent
from api.routes import alerts, chat, journal, portfolio, tools, watchlist
from infra.container import make_container
from settings import get_settings
from skills.adk_tools import bind_container


def create_app() -> FastAPI:
    settings = get_settings()
    container = make_container(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # The skill tools resolve from this (app-scoped) container.
        bind_container(container)
        llm = await container.get(LiteLlm)
        app.state.agent = MarketLensAgent(llm)
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

    for module in (chat, tools, portfolio, watchlist, alerts, journal):
        app.include_router(module.router, prefix="/api")

    setup_dishka(container, app)
    return app


app = create_app()
