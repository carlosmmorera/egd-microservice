from fastapi import APIRouter
from app.api.controllers import GameController
from app.api.schema import GameListResponse

router = APIRouter()

@router.get("/player/{pin}")
async def get_games_from_player(pin: int) -> GameListResponse:
    return await GameController.get_games_from_player(pin)
