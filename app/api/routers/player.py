from fastapi import APIRouter
from app.services.model import BasicPlayer
from app.api.controllers import PlayerController

router = APIRouter()

@router.get("/basic/{pin}")
async def basic_info(pin: str) -> BasicPlayer:
    return await PlayerController.get_basic_information(pin)