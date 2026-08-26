from pydantic import BaseModel
from typing import Optional, List

class Placement(BaseModel):
    id: int
    pinPlayer: int
    tournamentCode: str
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    countryCode: str
    club: Optional[str] = None
    placement: int
    gradeDeclared: str
    wonGames: int
    lostGames: int
    jigoGames: int
    precedentRating: float
    followingRating: float

class PlacementList(BaseModel):
    data: List[Placement] = []
    total: int