from functools import lru_cache
from pathlib import Path

import anthropic
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: SecretStr
    anthropic_base_url: str | None = None  # None → api.anthropic.com

    model_sonnet: str = "claude-sonnet-5-5"
    model_haiku: str = "claude-haiku-5-5"
    model_opus: str = "claude-opus-5-5"
    default_model: str = "claude-sonnet-5-5"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


@lru_cache
def get_client() -> anthropic.Anthropic:
    s = get_settings()
    return anthropic.Anthropic(
        base_url=s.anthropic_base_url,
        api_key=s.anthropic_api_key.get_secret_value(),
    )


settings = get_settings()
client = get_client()
