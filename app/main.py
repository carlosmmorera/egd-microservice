import sys
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger
from app.config import get_settings
from app.services import get_egd_client
from app.api.routers import player

def setup_logging():
    logger.remove()
    settings = get_settings()
    LOG_LEVEL = "DEBUG" if settings.DEBUG else "INFO"
    
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level= LOG_LEVEL,
        colorize=True
    )
    logger.add(
        "logs/microservice.log",
        rotation="10 MB",
        retention="14 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Initiating EGD Microservice...")
    yield
    
    logger.info("Shutting down EGD Microservice...")
    try:
        await asyncio.gather(
            get_egd_client.close(),
            return_exceptions=True
        )
        logger.info("All HTTP client connections closed successfully.")
    except Exception as e:
        logger.error(f"Error during clients shutdown: {e}")


app = FastAPI(
    title="EGD API Microservice",
    description="Microservice that connects to the European Go Database API for retrieving customized information",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(player.router, prefix="/player", tags=["player"])

#uv run uvicorn app.main:app --reload
#http://localhost:8000/docs