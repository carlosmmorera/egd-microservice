from app.services import get_egd_client
from app.api.schema import GameListResponse
from app.services.model import Game
from typing import List

class GameController:
    @staticmethod
    async def get_games_from_player(pin: int) -> GameListResponse:
        egd_client = await get_egd_client()
        game_list: List[Game] = await egd_client.get_all_player_games(pin)
        return {
            "games": game_list,
            "total": len(game_list)
        }
