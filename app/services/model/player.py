from pydantic import BaseModel
from typing import Optional
from app.services.model import PlacementList

class Biography(BaseModel):
    type: str
    biography: Optional[str] = None
    photo: Optional[str] = None

class Player(BaseModel):
    pin: int
    agaId: Optional[int] = None
    lastName: str
    firstName: str
    countryCode: str
    club: Optional[str] = None
    grade: str
    egfPlacement: Optional[int] = None
    rating: Optional[int] = None
    deltaRating: Optional[int] = None
    proposedGrade: Optional[str] = None
    totalTournaments: Optional[int] = None
    lastAppearance: Optional[str] = None
    placements: Optional[PlacementList] = None
    # biography: Optional[Biography] = None

class GraphQLPlayerData(BaseModel):
    player: Player

class GraphQLPlayerResponse(BaseModel):
    data: GraphQLPlayerData