"""The cited result shape every skill returns.

Skills never give advice — they return cited facts and structured data. The
synthesis agent turns these into a grounded answer; the MCP server and the
``/tools`` API return them verbatim.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from retrieval.interfaces import Citation


class Fact(BaseModel):
    text: str
    citation: Citation


class SkillResult(BaseModel):
    skill: str
    summary: str | None = None
    facts: list[Fact] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    citations: list[Citation] = Field(default_factory=list)
    note: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True)
