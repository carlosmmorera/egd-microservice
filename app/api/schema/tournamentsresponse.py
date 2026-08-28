from typing import List, Optional
from pydantic import BaseModel
from typing_extensions import TypedDict
from app.services.model import EGDTournament, TournamentClassEnum, TournamentStatusEnum, Placement, BasicPlayer

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
    def from_tournament(cls, tournament: EGDTournament) -> "BasicTournamentResponse":
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

class ExtendedPlacement(BaseModel):
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
    reset: bool = False
    firstTournament: bool = False
    precedentRating: float
    followingRating: float
    previousResetRating: Optional[float] = None
    deltaRating: float
    gamesDeltaRating: float
    resetDeltaRating: float

    @classmethod
    def from_placement(
        cls,
        placement: Placement,
        reset: bool,
        first_tournament: bool,
        prevResetRating: Optional[float] = None
    ) -> "ExtendedPlacement":
        delta_rating: float = placement.followingRating - placement.precedentRating
        if prevResetRating is not None:
            delta_rating += (placement.precedentRating - prevResetRating)

        return cls(
            id=placement.id,
            pinPlayer=placement.pinPlayer,
            tournamentCode=placement.tournamentCode,
            lastName=placement.lastName,
            firstName=placement.firstName,
            countryCode=placement.countryCode,
            club=placement.club,
            placement=placement.placement,
            gradeDeclared=placement.gradeDeclared,
            wonGames=placement.wonGames,
            lostGames=placement.lostGames,
            jigoGames=placement.jigoGames,
            reset=reset,
            firstTournament=first_tournament,
            precedentRating=placement.precedentRating,
            followingRating=placement.followingRating,
            previousResetRating=prevResetRating,
            deltaRating=delta_rating,
            gamesDeltaRating=placement.followingRating - placement.precedentRating,
            resetDeltaRating=delta_rating - (placement.followingRating - placement.precedentRating)
        )

class ExtendedTournamentResponse(BaseModel):
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
    totalGames: int
    numNewPlayers: int
    numResetPlayers: int
    deltaRating: float
    gamesDeltaRating: float
    resetDeltaRating: float
    status: Optional[TournamentStatusEnum] = None
    placements: Optional[List[ExtendedPlacement]] = None

    @classmethod
    def from_tournament(cls, tournament: EGDTournament, placements: List[ExtendedPlacement]) -> "ExtendedTournamentResponse":
        new_players: int = 0
        reset_players: int = 0
        for extended_plc in placements:
            if extended_plc.firstTournament:
                new_players += 1
            elif extended_plc.reset:
                reset_players += 1

        return cls(
            code=tournament.code,
            reliability=tournament.reliability,
            description=tournament.description,
            categoriesDescription=tournament.categoriesDescription,
            date=tournament.date,
            city=tournament.city,
            nation=tournament.nation,
            tournamentClass=tournament.tournamentClass,
            rounds=tournament.rounds,
            totalPlayers=tournament.totalPlayers,
            totalGames=sum([(plc.wonGames + plc.lostGames + plc.jigoGames) for plc in placements]),
            numNewPlayers=new_players,
            numResetPlayers=reset_players,
            deltaRating=sum([plc.deltaRating for plc in placements]),
            gamesDeltaRating=sum([plc.gamesDeltaRating for plc in placements]),
            resetDeltaRating=sum([plc.resetDeltaRating for plc in placements]),
            status=tournament.status,
            placements=placements
        )