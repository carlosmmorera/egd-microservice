from app.services import get_egd_client
from app.api.schema import GameListResponse
from app.services.model import Game
from typing import List, Optional
from datetime import date

class GameController:
    @staticmethod
    async def get_games_from_player(pin: int, start_date: Optional[date] = None, tournament_code: Optional[str] = None) -> GameListResponse:
        formatted_date = start_date.strftime("%Y-%m-%d 00:00:00") if start_date else None
        egd_client = await get_egd_client()
        game_list: List[Game] = await egd_client.game.get_player_games(pin, formatted_date, tournament_code)
        return {
            "games": game_list,
            "total": len(game_list)
        }

    @staticmethod
    async def get_game_by_id(id: int) -> Game:
        egd_client = await get_egd_client()
        return await egd_client.game.get_game_by_id(id)
