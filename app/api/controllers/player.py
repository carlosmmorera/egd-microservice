from app.services import get_egd_client
from app.services.model import BasicPlayer, Player

class PlayerController:
    @staticmethod
    async def get_basic_information(pin: int) -> BasicPlayer:
        egd_client = await get_egd_client()
        return await egd_client.get_basic_player_info(pin)

    @staticmethod
    async def get_information(pin: int) -> Player:
        egd_client = await get_egd_client()
        return await egd_client.get_player_information(pin)