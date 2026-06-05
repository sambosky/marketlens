"""ADK runner + event→SSE bridge.

A ``SequentialAgent`` runs the planner (tool routing) then the composer (cited
synthesis). ``stream()`` translates ADK events into the small event dicts the
SSE endpoint forwards to the UI: routing chips, collected sources, and the final
answer.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any

from google.adk.agents import SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.composition.agent import build_composition_agent
from agents.planning.agent import build_planning_agent

APP_NAME = "marketlens"
USER_ID = "local-user"


class MarketLensAgent:
    def __init__(self, llm: LiteLlm) -> None:
        root = SequentialAgent(
            name="marketlens",
            sub_agents=[build_planning_agent(llm), build_composition_agent(llm)],
        )
        self._sessions = InMemorySessionService()
        self._runner = Runner(agent=root, app_name=APP_NAME, session_service=self._sessions)

    async def stream(
        self, question: str, session_id: str | None = None
    ) -> AsyncIterator[dict[str, Any]]:
        session_id = session_id or uuid.uuid4().hex
        await self._sessions.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
        message = types.Content(role="user", parts=[types.Part(text=question)])

        citations: list[dict] = []
        seen: set[tuple] = set()

        async for event in self._runner.run_async(
            user_id=USER_ID, session_id=session_id, new_message=message
        ):
            for call in event.get_function_calls() or []:
                yield {"type": "routing", "tool": call.name, "args": dict(call.args or {})}

            for response in event.get_function_responses() or []:
                for citation in _extract_citations(response.response):
                    key = (citation.get("source"), citation.get("url"))
                    if key not in seen:
                        seen.add(key)
                        citations.append(citation)
                yield {"type": "tool_result", "tool": response.name}

            text = _event_text(event)
            if text and getattr(event, "author", None) == "composer":
                if event.is_final_response():
                    if citations:
                        yield {"type": "sources", "items": citations}
                    yield {"type": "final", "text": text}
                else:
                    yield {"type": "token", "text": text}

        yield {"type": "done"}

    async def ask(self, question: str) -> dict[str, Any]:
        answer = ""
        citations: list[dict] = []
        async for event in self.stream(question):
            if event["type"] == "final":
                answer = event["text"]
            elif event["type"] == "sources":
                citations = event["items"]
        return {"answer": answer, "citations": citations}


def _event_text(event: Any) -> str | None:
    content = getattr(event, "content", None)
    parts = getattr(content, "parts", None) if content else None
    if not parts:
        return None
    texts = [p.text for p in parts if getattr(p, "text", None)]
    return "".join(texts) if texts else None


def _extract_citations(response: Any) -> list[dict]:
    if not isinstance(response, dict):
        return []
    citations: list[dict] = list(response.get("citations") or [])
    for fact in response.get("facts") or []:
        citation = fact.get("citation") if isinstance(fact, dict) else None
        if citation:
            citations.append(citation)
    return citations
