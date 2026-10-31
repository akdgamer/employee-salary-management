from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables or a local .env file.

    Secrets have no defaults: the app refuses to start without them rather than
    running with a publicly known value.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://salary:salary@localhost:5432/salary"
    # HS256 with a short key can be brute-forced offline from any issued token.
    jwt_secret: str = Field(min_length=32)
    jwt_expire_hours: int = 12
    admin_username: str = "admin"
    admin_password: str
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
