from app.services import get_egd_client
from app.api.schema import GameListResponse
from app.services.model import Game
from typing import List

class GameController:
    @staticmethod
    async def get_games_from_player(pin: int) -> GameListResponse:
        egd_client = await get_egd_client()
        game_list: List[Game] = await egd_client.game.get_all_player_games(pin)
        return {
            "games": game_list,
            "total": len(game_list)
        }

    @staticmethod
    async def get_game_by_id(id: int) -> Game:
        egd_client = await get_egd_client()
        return await egd_client.game.get_game_by_id(id)
