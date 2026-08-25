import httpx
import asyncio
from app.services.egdclients import PlayerClient, GameClient

class EGDClient:
    _instancia = None
    _lock = None

    def __init__(self):
        self.__client: httpx.AsyncClient = httpx.AsyncClient(timeout=30.0)
        self._cache_lock = asyncio.Lock()
        self.player: PlayerClient = PlayerClient(self.__client)
        self.game: GameClient = GameClient(self.__client)

    @classmethod
    async def get_instance(cls):
        if cls._lock is None:
            cls._lock = asyncio.Lock()

        if cls._instancia is None:
            async with cls._lock:
                if cls._instancia is None:
                    cls._instancia = cls()
        return cls._instancia
    
    async def close(self):
        """Close httpx connections pool"""
        if self.__client:
            await self.__client.aclose()
    
async def get_egd_client() -> EGDClient:
    return await EGDClient.get_instance()