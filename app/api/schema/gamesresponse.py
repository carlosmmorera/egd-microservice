from typing import List
from typing_extensions import TypedDict
from app.services.model import Game

class GameListResponse(TypedDict):
    games: List[Game]
    total: int
