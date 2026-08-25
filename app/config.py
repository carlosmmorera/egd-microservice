from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "EGD-Microservice"
    DEBUG: bool = False

    EGD_BASE_URL: str = "https://europeangodatabase.eu/api"
    EGD_URL_GET_PLAYER_BY_PIN: str = "https://europeangodatabase.eu/EGD/GetPlayerDataByPIN.php"
    EGD_API_VERSION: str = "v2026.02"
    EGD_AUTH_TOKEN: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings() # type: ignore