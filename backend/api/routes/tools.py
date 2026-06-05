"""GET /tools and POST /tools/{name} — power the UI Tools panel.

These call the same skill functions the agent and MCP server use.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from skills.adk_tools import call_tool, tool_schemas

router = APIRouter()


class ToolCall(BaseModel):
    arguments: dict[str, Any] = Field(default_factory=dict)


@router.get("/tools")
async def list_tools() -> dict[str, Any]:
    return {"tools": tool_schemas()}


@router.post("/tools/{name}")
async def invoke_tool(name: str, body: ToolCall) -> dict[str, Any]:
    try:
        return await call_tool(name, body.arguments)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {name}") from exc
    except TypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
