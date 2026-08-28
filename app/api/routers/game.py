from fastapi import APIRouter, Query
from app.api.controllers import GameController
from app.api.schema import GameListResponse
from app.services.model import Game
from app.core.exceptions import BadRequestException
from datetime import date
from typing import Optional

router = APIRouter()

@router.get(
    "/",
    response_model=GameListResponse,
    response_model_exclude_none=True
)
async def get_games_from_player(
    pin: int = Query(..., description="Player Pin"),
    start_date: Optional[date] = Query(None, description="Start date (Format: YYYY-MM-DD)"),
    tournament_code: Optional[str] = Query(None, description="Tournament Code"),
    include_opponent_info: bool = Query(False, description="Include detailed opponent info")
) -> GameListResponse:
    if not start_date and not tournament_code:
        raise BadRequestException("start_date and tournament_code cannot be null at the same time")
    return await GameController.get_games_from_player(pin, start_date, tournament_code, include_opponent_info)

@router.get("/{id}")
async def get_game_by_id(id: int) -> Game:
    return await GameController.get_game_by_id(id)
