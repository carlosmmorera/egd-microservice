from fastapi import APIRouter
from app.services.model import BasicPlayer, Player
from app.api.controllers import PlayerController

router = APIRouter()

@router.get("/basic/{pin}")
async def basic_info(pin: int) -> BasicPlayer:
    return await PlayerController.get_basic_information(pin)

@router.get("/{pin}")
async def get_info(pin: int) -> Player:
    return await PlayerController.get_information(pin)