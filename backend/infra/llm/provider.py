"""Dishka provider for the LLM.

The model is created via ADK's ``LiteLlm`` wrapper, so the same agent code runs
on a **local Ollama** model (default, no key) or **Claude** (``anthropic/...``)
purely by configuration. The only difference is the model string and, for
Ollama, an ``api_base``.
"""

from __future__ import annotations

from dishka import Provider, Scope, provide
from google.adk.models.lite_llm import LiteLlm

from settings import Settings


def create_llm(settings: Settings) -> LiteLlm:
    extra: dict[str, object] = {}
    if settings.llm.provider == "ollama":
        # LiteLLM routes ``ollama_chat/*`` models to this base URL.
        extra["api_base"] = settings.llm.ollama_base_url
    return LiteLlm(
        model=settings.llm.litellm_model,
        temperature=settings.llm.temperature,
        **extra,
    )


class LLMProvider(Provider):
    scope = Scope.APP

    @provide
    def llm(self, settings: Settings) -> LiteLlm:
        return create_llm(settings)
