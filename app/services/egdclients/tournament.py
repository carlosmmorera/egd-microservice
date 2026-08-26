from loguru import logger
from app.services.egdclients import CoreClient
from app.services.model import EGDTournament, GraphQLTournamentResponse, TournamentList, GraphQLTournamentsResponse
from app.core.exceptions import InternalServerErrorException
from pydantic import ValidationError
from typing import List

class TournamentClient(CoreClient):
    async def get_tournament_by_code(self, code: str, include_placements: bool = True) -> EGDTournament:
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
        if include_placements:
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

    async def __get_tournaments_country_page(self, nation: str, dateFrom: str, page: int = 1, limit: int = 50) -> TournamentList:
        query = f"""
            query GetTournaments {{ 
                tournaments(
                    filter: {{ nation: \"{nation}\", dateFrom: \"{dateFrom}\" }}, 
                    pagination: {{ page: {page}, limit: {limit} }}
                ) {{
                    data {{
                        code
                        description
                        date
                        city
                        nation
                        tournamentClass
                        rounds
                        totalPlayers
                    }}
                    total
                    hasMorePages
                }}
            }}
        """

        payload = {
            "query": query,
            "operationName": "GetTournaments"
        }
        response = await self._graphql_query(payload)
        logger.info(f"Tournaments page {page} for nation {nation} successfully retrieved.")
        return GraphQLTournamentsResponse.model_validate(response.json()).data.tournaments

    async def get_tournaments_from(self, nation: str, dateFrom: str) -> List[EGDTournament]:
        all_tournaments: List[EGDTournament] = []
        current_page = 1
        
        logger.info(f"Starting to fetch all tournaments from {nation}")
        tournaments_page = await self.__get_tournaments_country_page(nation, dateFrom, current_page)
        all_tournaments.extend(tournaments_page.data)
        
        while tournaments_page.hasMorePages:
            current_page += 1
            tournaments_page = await self.__get_tournaments_country_page(nation, dateFrom, current_page)
            all_tournaments.extend(tournaments_page.data)

        logger.info(f"Successfully retrieved a total of {len(all_tournaments)} tournaments from {nation}")
        return all_tournaments