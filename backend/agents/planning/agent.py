from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from agents.planning.prompts import PLANNING_INSTRUCTION
from skills.adk_tools import build_adk_tools


def build_planning_agent(llm: LiteLlm) -> LlmAgent:
    """Tool-using router: triages the question, calls the right skill(s), and
    writes the cited findings to session state under ``research_findings``."""
    return LlmAgent(
        name="planner",
        model=llm,
        instruction=PLANNING_INSTRUCTION,
        tools=build_adk_tools(),
        output_key="research_findings",
    )
