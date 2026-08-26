from datetime import date
from typing import List
from app.services import get_egd_client
from app.api.schema import TournamentListResponse, BasicTournamentResponse
from app.services.model import EGDTournament

class TournamentController:
    @staticmethod
    async def get_by_code(code: str) -> EGDTournament:
        egd_client = await get_egd_client()
        return await egd_client.tournament.get_tournament_by_code(code)

    @staticmethod
    async def get_by_country_and_date(country_code: str, start_date: date) -> TournamentListResponse:
        """
        Obtiene una lista de torneos a partir de un país y una fecha determinada.
        """
        egd_client = await get_egd_client()
        tournamentList: List[BasicTournamentResponse] = [
            BasicTournamentResponse.from_tournament(t) for t in await egd_client.tournament.get_tournaments_from(
                nation=country_code, 
                dateFrom=start_date.strftime("%Y-%m-%d 00:00:00")
            )
        ]
        return {
            "tournaments": tournamentList,
            "total": len(tournamentList)
        }