from pydantic import BaseModel
from typing import Optional

class Player(BaseModel):
    pin: int
    agaId: int
    lastName: str
    firstName: str
    countryCode: str
    club: Optional[str] = None
    grade: str
    egfPlacement: Optional[int] = None
    rating: Optional[int] = None
    deltaRating: Optional[int] = None
    proposedGrade: str
    totalTournaments: Optional[int] = None
    lastAppearance: Optional[str] = None

class GraphQLPlayerData(BaseModel):
    player: Player

class GraphQLPlayerResponse(BaseModel):
    data: GraphQLPlayerData