import httpx
import asyncio
from loguru import logger
from typing import Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.exceptions import InternalServerErrorException, UnauthorizedException
from app.services.model import Game, GameList, GraphQLGamesResponse
from app.services.model import BasicPlayer, Player, GraphQLPlayerResponse
from app.config import get_settings

def should_retry(retry_state):
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        if isinstance(exception, httpx.RequestError):
            return True
        if isinstance(exception, httpx.HTTPStatusError) and exception.response.status_code >= 500:
            return True
    return False

with_retries = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=should_retry,
    reraise=True
)

class EGDClient:
    _instancia = None
    _lock = None

    def __init__(self):
        settings = get_settings()
        self.base_url: str = settings.EGD_BASE_URL
        self.url_basic_player: str = settings.EGD_URL_GET_PLAYER_BY_PIN
        self.version: str = settings.EGD_API_VERSION
        self.token: Optional[str] = settings.EGD_AUTH_TOKEN

        self.default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "EGD Microservice",
            "Accept": "application/json"
        }
        if self.token:
            self.default_headers["Authorization"] = f"Bearer {self.token}"

        self.client: httpx.AsyncClient = httpx.AsyncClient(
            timeout=30.0,
            headers=self.default_headers
        )
        self._cache_lock = asyncio.Lock()

    @classmethod
    async def get_instance(cls):
        if cls._lock is None:
            cls._lock = asyncio.Lock()

        if cls._instancia is None:
            async with cls._lock:
                if cls._instancia is None:
                    cls._instancia = cls()
        return cls._instancia
    
    async def close(self):
        """Close httpx connections pool"""
        if self.client:
            await self.client.aclose()
    
    def __is_authenticated(self) -> bool:
        return self.token is not None

    def __get_graphql_url(self) -> str:
        return f"{self.base_url}/{self.version}/graphql"

    @with_retries
    async def get_basic_player_info(self, pin: int) -> BasicPlayer:
        try:
            response = await self.client.get(f"{self.url_basic_player}?pin={pin}", headers=None)
            response.raise_for_status()
            logger.info(f"Basic player with Pin {pin} successfully retrieved.")
            response_data = response.json()
            return BasicPlayer.model_validate(response_data)
        except Exception as e:
            logger.error(f"Error retrieving basic player with pin {pin}: {e}")
            raise InternalServerErrorException(f"Error retrieving basic player with pin {pin}")

    @with_retries
    async def get_player_information(self, pin: int) -> Player:
        if not self.__is_authenticated():
            logger.error("Authentication token is missing for getting player information")
            raise UnauthorizedException("Unauthorized operation")

        query = """
        query GetPlayer($pin: Int!) { 
            player(pin: $pin) {
                pin
                agaId
                lastName
                firstName
                countryCode
                club
                grade
                egfPlacement
                rating
                deltaRating
                proposedGrade
                totalTournaments
                lastAppearance
            }
        }
        """
        payload = {
            "query": query,
            "variables": {
                "pin": pin
            }
        }

        try:
            response = await self.client.post(self.__get_graphql_url(), json=payload)
            try:
                response_data = response.json()
            except ValueError:
                logger.error(f"Non-JSON response for pin {pin}. Raw response: {response.text}")
                response.raise_for_status()
                
                raise InternalServerErrorException(f"Invalid non-JSON response from server for pin {pin}")

            if "errors" in response_data:
                logger.error(f"GraphQL returned errors for player with pin {pin}: {response_data['errors']}")
                raise InternalServerErrorException(f"GraphQL error retrieving player with {pin}")
            response.raise_for_status()

            logger.info(f"Player with Pin {pin} successfully retrieved.")
            return GraphQLPlayerResponse.model_validate(response_data).data.player

        except InternalServerErrorException:
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error retrieving player with pin {pin}: {e.response.text}")
            raise InternalServerErrorException(f"Error retrieving player with pin {pin}")
        except Exception as e:
            logger.error(f"Error retrieving player with pin {pin}: {e}")
            raise InternalServerErrorException(f"Error retrieving player with pin {pin}")

    @with_retries
    async def __get_player_games_page(self, pin: int, page: int = 1, limit: int = 50) -> GameList:
        if not self.__is_authenticated():
            logger.error("Authentication token is missing for getting player games")
            raise UnauthorizedException("Unauthorized operation")

        query = """
        query GetPlayerGames($filter: GameFilterInput, $order: GameOrderInput, $pagination: PaginationInput!) { 
            games(filter: $filter, order: $order, pagination: $pagination) {
                data {
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
                total
                hasMorePages
            }
        }
        """

        
        payload = {
            "query": query,
            "operationName": "GetPlayerGames",
            "variables": {
                "filter": {
                    "pinPlayer": pin
                },
                "order": {
                    "field": "date",
                    "direction": "DESC"
                },
                "pagination": {
                    "page": page,
                    "limit": limit
                }
            }
        }

        try:
            response = await self.client.post(self.__get_graphql_url(), json=payload)
            try:
                response_data = response.json()
            except ValueError:
                logger.error(f"Non-JSON response for games of pin {pin}. Raw response: {response.text}")
                response.raise_for_status()
                raise InternalServerErrorException(f"Invalid non-JSON response from server for games of pin {pin}")

            if "errors" in response_data:
                logger.error(f"GraphQL returned errors for games with pin {pin}: {response_data['errors']}")
                raise InternalServerErrorException(f"GraphQL error retrieving games with {pin}")
            
            response.raise_for_status()

            logger.info(f"Games page {page} for Pin {pin} successfully retrieved.")
            return GraphQLGamesResponse.model_validate(response_data).data.games

        except InternalServerErrorException:
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error retrieving games with pin {pin}: {e.response.text}")
            raise InternalServerErrorException(f"Error retrieving games with pin {pin}")
        except Exception as e:
            logger.error(f"Error retrieving games with pin {pin}: {e}")
            raise InternalServerErrorException(f"Error retrieving games with pin {pin}")

    async def get_all_player_games(self, pin: int) -> List[Game]:
        all_games: List[Game] = []
        current_page = 1
        
        logger.info(f"Starting to fetch all games for pin {pin}")
        games_page = await self.__get_player_games_page(pin=pin, page=current_page)
        all_games.extend(games_page.data)
        
        while games_page.hasMorePages:
            current_page += 1
            games_page = await self.__get_player_games_page(pin=pin, page=current_page)
            all_games.extend(games_page.data)

        logger.info(f"Successfully retrieved a total of {len(all_games)} games for pin {pin}")
        return all_games
        
async def get_egd_client() -> EGDClient:
    return await EGDClient.get_instance()