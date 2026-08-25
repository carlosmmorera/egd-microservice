from pydantic import BaseModel
from typing import Optional
from enum import Enum

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

class Tournament(BaseModel):
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
    status: TournamentStatusEnum

class GraphQLTournamentData(BaseModel):
    tournament: Tournament

class GraphQLTournamentResponse(BaseModel):
    data: GraphQLTournamentData