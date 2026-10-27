from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_SECRET_KEY = "development-only-secret-key-change-me-000000"


class Settings(BaseSettings):
    """Настройки приложения, читаются из переменных окружения и .env."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Спортивный клуб — API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://sports_club:sports_club@localhost:5433/sports_club"

    secret_key: str = _DEV_SECRET_KEY
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    payment_provider: str = "mock"
    default_currency: str = "RUB"

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        insecure_keys = {"change-me-in-production", _DEV_SECRET_KEY}
        if self.environment == "production" and (
            self.secret_key in insecure_keys or len(self.secret_key) < 32
        ):
            raise ValueError("SECRET_KEY must be changed in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
