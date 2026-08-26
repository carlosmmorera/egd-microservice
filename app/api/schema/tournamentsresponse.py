from typing import List, Optional
from pydantic import BaseModel
from typing_extensions import TypedDict
from app.services.model import EGDTournament, TournamentClassEnum

class BasicTournamentResponse(BaseModel):
    code: str
    description: Optional[str] = None
    date: str
    city: str
    nation: str
    tournamentClass: TournamentClassEnum
    rounds: int
    totalPlayers: Optional[int] = None

    @classmethod
    def from_tournament(cls, tournament: EGDTournament):
        return cls(
            code=tournament.code,
            description=tournament.description,
            date=tournament.date,
            city=tournament.city,
            nation=tournament.nation,
            tournamentClass=tournament.tournamentClass,
            rounds=tournament.rounds,
            totalPlayers=tournament.totalPlayers
        )

class TournamentListResponse(TypedDict):
    tournaments: List[BasicTournamentResponse]
    total: int
