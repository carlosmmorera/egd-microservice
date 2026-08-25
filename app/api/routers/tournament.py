from fastapi import APIRouter
from app.services.model import Tournament
from app.api.controllers import TournamentController

router = APIRouter()

@router.get("/{code}")
async def get_tournament_by_code(code: str) -> Tournament:
    return await TournamentController.get_by_code(code)