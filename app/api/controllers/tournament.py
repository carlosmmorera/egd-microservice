from datetime import date
from typing import List
from app.services import get_egd_client
from app.api.schema import TournamentListResponse, BasicTournamentResponse, ExtendedPlacement, ExtendedTournamentResponse
from app.services.model import EGDTournament, Placement, Player
from app.api.controllers import PlayerController
from datetime import datetime
from loguru import logger

class TournamentController:
    @staticmethod
    async def _extend_placement_information(placement: Placement) -> ExtendedPlacement:
        if placement.precedentRating is None or placement.precedentRating % 100 != 0:
            return ExtendedPlacement.from_placement(placement, False, False)

        player_info: Player = await PlayerController.get_information(placement.pinPlayer)

        ordered_placements: List[Placement] = []
        if player_info.placements is not None:
            ordered_placements = sorted(player_info.placements.data, key=lambda x: x.tournamentCode)

        position = next((i for i, placemnt in enumerate(ordered_placements) if placemnt.tournamentCode == placement.tournamentCode), -1)
        if position == -1:
            return ExtendedPlacement.from_placement(placement, False, False)
        elif position == 0:
            return ExtendedPlacement.from_placement(placement, False, True)
        elif ordered_placements[position].precedentRating != ordered_placements[position - 1].followingRating:
            return ExtendedPlacement.from_placement(placement, True, False, ordered_placements[position - 1].followingRating)

        return ExtendedPlacement.from_placement(placement, False, False)

    @staticmethod
    async def get_by_code(code: str) -> ExtendedTournamentResponse:
        egd_client = await get_egd_client()
        egd_tournament: EGDTournament = await egd_client.tournament.get_tournament_by_code(code)
        ext_placements: List[ExtendedPlacement] = []
        if egd_tournament.placements is not None:
            ext_placements = [await TournamentController._extend_placement_information(plc) for plc in egd_tournament.placements.data]

        return ExtendedTournamentResponse.from_tournament(egd_tournament, ext_placements)

    @staticmethod
    async def get_by_country_and_date(country_code: str, start_date: date) -> TournamentListResponse:
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

    @staticmethod
    async def get_by_player_and_date(pin: int, start_date: date) -> TournamentListResponse:
        player_info: Player = await PlayerController.get_information(pin)

        if player_info.placements is None or len(player_info.placements.data) < 1:
            return {
                "tournaments": [],
                "total": 0
            }

        tournamentList: List[BasicTournamentResponse] = []
        egd_client = await get_egd_client()

        for placement in player_info.placements.data:
            t_code = placement.tournamentCode

            # Tournament Code format: <letter> + <date in format YYMMDD> + <letter>
            if len(t_code) == 8:
                date_str = t_code[1:7]
                try:
                    tournament_date = datetime.strptime(date_str, "%y%m%d").date()
                    if tournament_date > start_date:
                        tournamet: EGDTournament = await egd_client.tournament.get_tournament_by_code(t_code)
                        tournamentList.append(BasicTournamentResponse.from_tournament(tournamet))
                        
                except ValueError:
                    logger.error(f"Error processing tournament code {t_code}")

        return {
            "tournaments": tournamentList,
            "total": len(tournamentList)
        }