from abc import ABC
import httpx
from loguru import logger
from typing import Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.exceptions import InternalServerErrorException, UnauthorizedException
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

class CoreClient(ABC):
    def __init__(self, http_client:  httpx.AsyncClient):
        settings = get_settings()
        self.base_url: str = settings.EGD_BASE_URL
        self.url_basic_player: str = settings.EGD_URL_GET_PLAYER_BY_PIN
        self.version: str = settings.EGD_API_VERSION
        self.token: Optional[str] = settings.EGD_AUTH_TOKEN

        self.default_headers = {
            "Content-Type": "application/json",
            "User-Agent": "EGD Microservice",
            "Accept": "application/json"
        }
        if self.token:
            self.default_headers["Authorization"] = f"Bearer {self.token}"

        self.client = http_client
    
    def __is_authenticated(self) -> bool:
        return self.token is not None

    def __get_graphql_url(self) -> str:
        return f"{self.base_url}/{self.version}/graphql"

    @with_retries
    async def _graphql_query(self, payload: Any) -> httpx.Response:
        if not self.__is_authenticated():
            logger.error("Authentication GraphQL token is missing.")
            raise UnauthorizedException("Unauthorized operation")

        try:
            response = await self.client.post(self.__get_graphql_url(), headers=self.default_headers, json=payload)
            try:
                response_data = response.json()
            except ValueError:
                logger.error(f"Non-JSON response. Raw response: {response.text}")
                response.raise_for_status()
                
                raise InternalServerErrorException("Invalid non-JSON response from server")

            if "errors" in response_data:
                logger.error(f"GraphQL returned errors: {response_data['errors']}")
                raise InternalServerErrorException("GraphQL error")
            response.raise_for_status()

            return response

        except InternalServerErrorException:
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error: {e.response.text}")
            raise InternalServerErrorException("HTTP Error")
        except Exception as e:
            logger.error(f"Unexpected exception: {e}")
            raise InternalServerErrorException("Unexpected exception")