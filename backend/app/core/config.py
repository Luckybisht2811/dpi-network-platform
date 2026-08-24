from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "DPI Network Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/dpi_db"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Network capture
    CAPTURE_INTERFACE: str = "Ethernet"  # apne network interface ka naam yahan

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()