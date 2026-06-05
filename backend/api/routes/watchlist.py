"""Watchlist routes (non-executing action), Dishka-injected."""

from __future__ import annotations

from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter
from pydantic import BaseModel

from skills.watchlist import WatchlistSkill

router = APIRouter(route_class=DishkaRoute)


class WatchlistAdd(BaseModel):
    ticker: str
    note: str | None = None


@router.get("/watchlist")
async def list_watchlist(skill: FromDishka[WatchlistSkill]) -> dict[str, Any]:
    return (await skill.list()).as_dict()


@router.post("/watchlist")
async def add_watchlist(body: WatchlistAdd, skill: FromDishka[WatchlistSkill]) -> dict[str, Any]:
    return (await skill.add(body.ticker, body.note)).as_dict()


@router.delete("/watchlist/{ticker}")
async def remove_watchlist(ticker: str, skill: FromDishka[WatchlistSkill]) -> dict[str, Any]:
    return (await skill.remove(ticker)).as_dict()
