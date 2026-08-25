from app.services import get_egd_client
from app.services.model import BasicPlayer

class PlayerController:
    @staticmethod
    async def get_basic_information(pin: str) -> BasicPlayer:
        egd_client = await get_egd_client()
        return await egd_client.get_basic_player_info(pin)