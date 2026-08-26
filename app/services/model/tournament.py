from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from app.services.model import PlacementList

class TournamentClassEnum(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class TournamentStatusEnum(str, Enum):
    Rejected = "Rejected"
    Approved = "Approved"
    AwaitingValidation = "AwaitingValidation"
    Validated = "Validated"

class EGDTournament(BaseModel):
    code: str
    reliability: Optional[int] = None
    description: Optional[str] = None
    categoriesDescription: Optional[str] = None
    date: str
    city: str
    nation: str
    tournamentClass: TournamentClassEnum
    rounds: int
    totalPlayers: Optional[int] = None
    status: Optional[TournamentStatusEnum] = None
    placements: Optional[PlacementList] = None

class TournamentList(BaseModel):
    data: List[EGDTournament]
    total: int
    hasMorePages: bool

class GraphQLTournamentData(BaseModel):
    tournament: EGDTournament

class GraphQLTournamentResponse(BaseModel):
    data: GraphQLTournamentData

class GraphQLTournamentsData(BaseModel):
    tournaments: TournamentList

class GraphQLTournamentsResponse(BaseModel):
    data: GraphQLTournamentsData