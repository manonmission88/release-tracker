import logging
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATABASE_URL = "postgresql+psycopg://release_tracker:release_tracker@localhost:5432/release_tracker"
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


class Settings(BaseSettings):
    database_url: str = DEFAULT_DATABASE_URL
    debug: bool = False
    jwt_secret_key: SecretStr = Field(min_length=12)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


def configure_logging(*, debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format=LOG_FORMAT)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
