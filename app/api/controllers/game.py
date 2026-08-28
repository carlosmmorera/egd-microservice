from typing import List, Optional, Dict, Set
from datetime import date
from collections import defaultdict
from app.services import get_egd_client
from app.api.schema import GameListResponse, ExtendedGame, ExtendedTournamentResponse
from app.services.model import Game
from app.api.controllers import TournamentController

class GameController:
    @staticmethod
    async def get_games_from_player(
        pin: int, 
        start_date: Optional[date] = None, 
        tournament_code: Optional[str] = None,
        include_oponent_info: bool = False
    ) -> GameListResponse:
        formatted_date = start_date.strftime("%Y-%m-%d 00:00:00") if start_date else None
        egd_client = await get_egd_client()
        game_list: List[Game] = await egd_client.game.get_player_games(pin, formatted_date, tournament_code)
        if not include_oponent_info:
            return GameListResponse(
                games=game_list,
                total=len(game_list)
            )

        tournament_games: Dict[str, List[ExtendedGame]] = defaultdict(list)
        tournament_players: Dict[str, Set] = defaultdict(set)
        for game in game_list:
            tournament_games[game.tournamentCode].append(ExtendedGame.model_validate(game.model_dump()))
            tournament_players[game.tournamentCode].add(game.pinPlayer1)
            tournament_players[game.tournamentCode].add(game.pinPlayer2)

        extended_game_list: List[ExtendedGame] = []

        for t_code, games in tournament_games.items():
            tournament: ExtendedTournamentResponse = await TournamentController.get_by_code(t_code)
            if tournament.placements is not None:
                placement_by_pin = {
                    placement.pinPlayer: placement for placement in tournament.placements 
                    if placement.pinPlayer in tournament_players[t_code]
                }

                for ext_game in games:
                    if ext_game.pinPlayer1 in placement_by_pin:
                        ext_game.add_player1(placement_by_pin[ext_game.pinPlayer1])
                    if ext_game.pinPlayer2 in placement_by_pin:
                        ext_game.add_player2(placement_by_pin[ext_game.pinPlayer2])

            extended_game_list.extend(games)

        return GameListResponse(
            games=extended_game_list,
            total=len(extended_game_list)
        )

    @staticmethod
    async def get_game_by_id(id: int) -> Game:
        egd_client = await get_egd_client()
        return await egd_client.game.get_game_by_id(id)
