from typing import Sequence, Union, Optional, Self
from typing_extensions import TypedDict
from pydantic import BaseModel
from app.services.model import Game, Placement

class PlayerInfo(BaseModel):
    lastName: Optional[str] = None
    firstName: Optional[str] = None
    countryCode: str
    club: Optional[str] = None
    gradeDeclared: str
    precedentRating: float

    @classmethod
    def from_extended_placement(cls, placement: Placement) -> "PlayerInfo":
        return cls(
            lastName=placement.lastName,
            firstName=placement.firstName,
            countryCode=placement.countryCode,
            club=placement.club,
            gradeDeclared=placement.gradeDeclared,
            precedentRating=placement.precedentRating
        )

class ExtendedGame(Game):
    tournamentName: Optional[str] = None
    player1: Optional[PlayerInfo] = None
    player2: Optional[PlayerInfo] = None

    def add_player1(self, placement: Placement) -> Self:
        self.player1 = PlayerInfo.from_extended_placement(placement)
        return self

    def add_player2(self, placement: Placement) -> Self:
        self.player2 = PlayerInfo.from_extended_placement(placement)
        return self

class GameListResponse(TypedDict):
    games: Sequence[Union[ExtendedGame, Game]]
    total: int
