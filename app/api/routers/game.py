from fastapi import APIRouter, Query
from app.api.controllers import GameController
from app.api.schema import GameListResponse
from app.services.model import Game
from datetime import date

router = APIRouter()

@router.get("/")
async def get_games_from_player(
    pin: int = Query(..., description="Player Pin"),
    start_date: date = Query(..., description="Start date (Format: YYYY-MM-DD)")
) -> GameListResponse:
    return await GameController.get_games_from_player(pin, start_date)

@router.get("/{id}")
async def get_game_by_id(id: int) -> Game:
    return await GameController.get_game_by_id(id)
