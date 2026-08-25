from loguru import logger
from app.services.egdclients import CoreClient
from app.services.model import Tournament, GraphQLTournamentResponse
from app.core.exceptions import InternalServerErrorException
from pydantic import ValidationError

class TournamentClient(CoreClient):
    async def get_tournament_by_code(self, code: str) -> Tournament:
        query = """
        query GetTournament($code: String!) { 
            tournament(code: $code) {
                code
                reliability
                description
                categoriesDescription
                date
                city
                nation
                tournamentClass
                rounds
                totalPlayers
                status
            }
        }
        """
        payload = {
            "query": query,
            "variables": {
                "code": code
            }
        }
        response = await self._graphql_query(payload)
        logger.info(f"Tournament with code {code} successfully retrieved.")
        try:
            return GraphQLTournamentResponse.model_validate(response.json()).data.tournament
        except ValidationError as e:
            logger.error(f"Validation error retrieving tournament with code {code}\nObtained {response.json()}\nError information: {e}")
            raise InternalServerErrorException(f"Validation error retrieving tournament with code {code}")