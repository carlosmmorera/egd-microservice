import httpx
import asyncio
from loguru import logger
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.exceptions import InternalServerErrorException
from app.services.model import BasicPlayer
from app.config import get_settings

def should_retry(retry_state):
    if retry_state.outcome.failed:
        exception = retry_state.outcome.exception()
        if isinstance(exception, httpx.RequestError):
            return True
        if isinstance(exception, httpx.HTTPStatusError) and exception.response.status_code >= 500:
            return True
    return False

with_retries = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=should_retry,
    reraise=True
)

class EGDClient:
    _instancia = None
    _lock = None

    def __init__(self):
        settings = get_settings()
        self.base_url: str = settings.EGD_BASE_URL
        self.url_basic_player: str = settings.EGD_URL_GET_PLAYER_BY_PIN
        self.version: str = settings.EGD_API_VERSION
        self.token: Optional[str] = settings.EGD_AUTH_TOKEN

        self.client: httpx.AsyncClient = httpx.AsyncClient(timeout=20.0)
        self._cache_lock = asyncio.Lock()

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
        if self.client:
            await self.client.aclose()
    
    def __is_authenticated(self) -> bool:
        return self.token is not None

    @with_retries
    async def get_basic_player_info(self, pin: str) -> BasicPlayer:
        try:
            response = await self.client.get(f"{self.url_basic_player}?pin={pin}")
            response.raise_for_status()
            logger.info(f"Basic player with Pin {pin} successfully retrieved.")
            response_data = response.json()
            return BasicPlayer.model_validate(response_data)
        except Exception as e:
            logger.error(f"Error retrieving basic player with pin {pin}: {e}")
            raise InternalServerErrorException(f"Error retrieving basic player with pin {pin}")
        
async def get_egd_client() -> EGDClient:
    return await EGDClient.get_instance()