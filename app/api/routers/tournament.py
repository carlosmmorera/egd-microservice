from fastapi import APIRouter, Query
from typing import Optional
from datetime import date
from app.api.controllers import TournamentController
from app.api.schema import TournamentListResponse, ExtendedTournamentResponse
from app.core.exceptions import BadRequestException

router = APIRouter()

@router.get("/")
async def get_tournaments(
    start_date: date = Query(..., description="Start date (Format: YYYY-MM-DD)"),
    country_code: Optional[str] = Query(None, description="Country Code (ej. ES, FR, IT)"),
    pin: Optional[int] = Query(None, description="Player PIN")
) -> TournamentListResponse:
    if country_code is None and pin is None:
        raise BadRequestException("country_code and pin cannot be null at the same time")

    if pin is not None:
        return await TournamentController.get_by_player_and_date(pin, start_date)

    return await TournamentController.get_by_country_and_date(country_code, start_date) # type: ignore

@router.get("/{code}")
async def get_tournament_by_code(code: str) -> ExtendedTournamentResponse:
    return await TournamentController.get_by_code(code)