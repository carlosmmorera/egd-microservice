from fastapi import APIRouter, Query
from datetime import date
from app.services.model import EGDTournament
from app.api.controllers import TournamentController
from app.api.schema import TournamentListResponse

router = APIRouter()

@router.get("/")
async def get_tournaments(
    country_code: str = Query(..., description="Country Code (ej. ES, FR, IT)"),
    start_date: date = Query(..., description="Start date (Format: YYYY-MM-DD)")
) -> TournamentListResponse:
    return await TournamentController.get_by_country_and_date(country_code, start_date)

@router.get("/{code}")
async def get_tournament_by_code(code: str) -> EGDTournament:
    return await TournamentController.get_by_code(code)