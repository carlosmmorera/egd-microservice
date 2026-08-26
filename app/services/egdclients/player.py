import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from app.services.egdclients import CoreClient
from app.core.exceptions import InternalServerErrorException
from app.services.model import BasicPlayer, Player, GraphQLPlayerResponse

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

class PlayerClient(CoreClient):
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

    async def get_player_information(self, pin: int, include_placements: bool = True) -> Player:
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
        if include_placements:
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
                        placements {
                            data {
                                id
                                pinPlayer
                                tournamentCode
                                lastName
                                firstName
                                countryCode
                                club
                                placement
                                gradeDeclared
                                wonGames
                                lostGames
                                jigoGames
                                precedentRating
                                followingRating
                            }
                            total
                        }
                    }
                }
            """
        payload = {
            "query": query,
            "variables": {
                "pin": pin
            }
        }
        response = await self._graphql_query(payload)
        logger.info(f"Player with pin {pin} successfully retrieved.")
        return GraphQLPlayerResponse.model_validate(response.json()).data.player
