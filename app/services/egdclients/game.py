from loguru import logger
from typing import List, Optional
from app.services.egdclients import CoreClient
from app.services.model import Game, GameList, GraphQLGamesResponse, GraphQLGameResponse
from app.core.exceptions import InternalServerErrorException, NotFoundException
from pydantic import ValidationError

class GameClient(CoreClient):
    async def get_game_by_id(self, id: int) -> Game:
        query = """
        query GetGame($id: Int!) { 
            game(id: $id) {
                id
                tournamentCode
                date
                round
                pinPlayer1
                color1
                pinPlayer2
                color2
                handicap
                result
                sgfCode
            }
        }
        """
        payload = {
            "query": query,
            "variables": {
                "id": id
            }
        }
        response = await self._graphql_query(payload)
        logger.info(f"Game with id {id} successfully retrieved.")
        try:
            response_data = response.json()
            if "data" not in response_data or "game" not in response_data["data"] or response_data["data"]["game"] is None:
                raise NotFoundException(f"Game with id {id} not found")
            return GraphQLGameResponse.model_validate(response.json()).data.game
        except ValidationError as e:
            logger.error(f"Validation error retrieving game with id {id}\nObtained {response.json()}\nError information: {e}")
            raise InternalServerErrorException(f"Validation error retrieving game with id {id}")

    async def __get_player_games_page(
        self, 
        pin: int, 
        dateFrom: Optional[str] = None, 
        tournamentCode: Optional[str] = None, 
        page: int = 1, 
        limit: int = 50
    ) -> GameList:
        filters = [f"pinPlayer: {pin}"]
        
        if dateFrom:
            filters.append(f'dateFrom: "{dateFrom}"')
        if tournamentCode:
            filters.append(f'tournamentCode: "{tournamentCode}"')
        filter_str = ", ".join(filters)
        
        query = f"""
        query GetPlayerGames {{ 
            games(
                filter: {{ {filter_str} }}, 
                pagination: {{ page: {page}, limit: {limit} }}
            ) {{
                data {{
                    id
                    tournamentCode
                    date
                    round
                    pinPlayer1
                    color1
                    pinPlayer2
                    color2
                    handicap
                    result
                    sgfCode
                }}
                total
                hasMorePages
            }}
        }}
        """

        payload = {
            "query": query,
            "operationName": "GetPlayerGames"
        }
        response = await self._graphql_query(payload)
        logger.info(f"Games page {page} for Pin {pin} successfully retrieved.")
        return GraphQLGamesResponse.model_validate(response.json()).data.games

    async def get_player_games(
        self, 
        pin: int, 
        dateFrom: Optional[str] = None, 
        tournamentCode: Optional[str] = None
    ) -> List[Game]:
        all_games: List[Game] = []
        current_page = 1
        
        logger.info(f"Starting to fetch all games for pin {pin}")
        games_page = await self.__get_player_games_page(
            pin=pin, dateFrom=dateFrom, tournamentCode=tournamentCode, page=current_page
        )
        all_games.extend(games_page.data)
        
        while games_page.hasMorePages:
            current_page += 1
            games_page = await self.__get_player_games_page(pin=pin, dateFrom=dateFrom, page=current_page)
            all_games.extend(games_page.data)

        logger.info(f"Successfully retrieved a total of {len(all_games)} games for pin {pin}")
        return all_games