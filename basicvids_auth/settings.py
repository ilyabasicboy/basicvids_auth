from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "sqlite:///./data/database.db"
    REDIS_URL: str = "redis://localhost:6379/2"
    DEBUG: bool = False
    EMAIL_CODE_EXPIRE_MINUTES: int = 10
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAIL_FROM: str = "noreply@basicvids.local"
    REFRESH_TOKEN_COOKIE_NAME: str = "basicvids_refresh_token"
    REFRESH_TOKEN_COOKIE_PATH: str = "/api/v1/auth"
    REFRESH_TOKEN_COOKIE_SECURE: bool = False
    REFRESH_TOKEN_COOKIE_SAMESITE: str = "lax"
    REFRESH_TOKEN_REVOKED_RETENTION_DAYS: int = 30
    REFRESH_TOKEN_CLEANUP_CRON: str = "0 8 * * *"

    model_config = SettingsConfigDict(
        env_file="./data/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

try:
    settings = Settings()
except Exception as e:
    print(e)
