# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


"""
The configuration.
"""


from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLALCHEMY_SOURCE_DATABASE_URL: str
    SQLALCHEMY_TEST_DATABASE_URL: str
    model_config = SettingsConfigDict(env_file=".env")


__settings: Settings | None = None
"""The configuration settings."""


@lru_cache
def get_settings() -> Settings:
    """Returns the configuration settings."""
    global __settings
    if __settings is None:
        __settings = Settings()
    return __settings


def set_settings(settings: Settings) -> None:
    """Sets the configuration settings."""
    global __settings
    get_settings.cache_clear()
    __settings = settings
