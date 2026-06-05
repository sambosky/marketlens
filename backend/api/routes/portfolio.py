"""Portfolio dashboard route (read-only), Dishka-injected."""

from __future__ import annotations

from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from skills.portfolio import PortfolioSkill

router = APIRouter(route_class=DishkaRoute)


@router.get("/portfolio")
async def get_portfolio(
    skill: FromDishka[PortfolioSkill], ticker: str | None = None
) -> dict[str, Any]:
    return (await skill.run(ticker)).as_dict()
