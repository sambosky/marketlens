from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from agents.composition.prompts import COMPOSITION_INSTRUCTION


def build_composition_agent(llm: LiteLlm) -> LlmAgent:
    """Synthesizes the cited, non-advisory final answer from session state."""
    return LlmAgent(
        name="composer",
        model=llm,
        instruction=COMPOSITION_INSTRUCTION,
    )
