"""Trade-journal routes (non-executing action), Dishka-injected."""

from __future__ import annotations

from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from pydantic import BaseModel

from skills.journal import JournalSkill

router = APIRouter(route_class=DishkaRoute)


class JournalCreate(BaseModel):
    ticker: str
    note: str
    action: str | None = None
    rationale: str | None = None


@router.get("/journal")
async def list_journal(
    skill: FromDishka[JournalSkill], ticker: str | None = None
) -> dict[str, Any]:
    return (await skill.list(ticker)).as_dict()


@router.post("/journal")
async def create_journal(body: JournalCreate, skill: FromDishka[JournalSkill]) -> dict[str, Any]:
    return (await skill.log(body.ticker, body.note, body.action, body.rationale)).as_dict()
