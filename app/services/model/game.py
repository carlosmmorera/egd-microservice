from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class GameColorEnum(str, Enum):
    Black = "Black"
    White = "White"

class Game(BaseModel):
    id: int
    tournamentCode: str
    date: Optional[str] = None
    round: int
    pinPlayer1: int
    color1: Optional[GameColorEnum] = None
    pinPlayer2: int
    color2: Optional[GameColorEnum] = None
    handicap: int
    result: str
    sgfCode: Optional[str] = None

class GraphQLGameData(BaseModel):
    game: Game

class GraphQLGameResponse(BaseModel):
    data: GraphQLGameData

class GameList(BaseModel):
    data: List[Game]
    total: int
    hasMorePages: bool

class GraphQLGamesData(BaseModel):
    games: GameList

class GraphQLGamesResponse(BaseModel):
    data: GraphQLGamesData