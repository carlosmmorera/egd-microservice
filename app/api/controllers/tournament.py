from app.services import get_egd_client
from app.services.model import Tournament

class TournamentController:
    @staticmethod
    async def get_by_code(code: str) -> Tournament:
        egd_client = await get_egd_client()
        return await egd_client.tournament.get_tournament_by_code(code)
