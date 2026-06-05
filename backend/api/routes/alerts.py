"""Price-alert routes (non-executing action), Dishka-injected."""

from __future__ import annotations

from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from pydantic import BaseModel

from skills.alerts import AlertsSkill

router = APIRouter(route_class=DishkaRoute)


class AlertCreate(BaseModel):
    ticker: str
    threshold: float
    direction: str  # "above" | "below"


@router.get("/alerts")
async def list_alerts(skill: FromDishka[AlertsSkill]) -> dict[str, Any]:
    return (await skill.list()).as_dict()


@router.post("/alerts")
async def create_alert(body: AlertCreate, skill: FromDishka[AlertsSkill]) -> dict[str, Any]:
    return (await skill.set_alert(body.ticker, body.threshold, body.direction)).as_dict()
