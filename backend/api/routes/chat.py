"""POST /ask — streams the agent run (routing chips, sources, final answer) as SSE."""

from __future__ import annotations

import json

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    session_id: str | None = None


@router.post("/ask")
async def ask(body: AskRequest, request: Request) -> EventSourceResponse:
    agent = request.app.state.agent

    async def event_stream():
        async for event in agent.stream(body.question, body.session_id):
            yield {"event": event["type"], "data": json.dumps(event)}

    return EventSourceResponse(event_stream())
