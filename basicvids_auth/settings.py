from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "sqlite:///./data/database.db"

    model_config = SettingsConfigDict(
        env_file="./data/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

try:
    settings = Settings()
except Exception as e:
    print(e)
