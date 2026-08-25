from fastapi import APIRouter
from app.api.controllers import GameController
from app.api.schema import GameListResponse
from app.services.model import Game

router = APIRouter()

@router.get("/player/{pin}")
async def get_games_from_player(pin: int) -> GameListResponse:
    return await GameController.get_games_from_player(pin)

@router.get("/{id}")
async def get_game_by_id(id: int) -> Game:
    return await GameController.get_game_by_id(id)
