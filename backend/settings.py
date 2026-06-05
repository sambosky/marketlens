"""Application configuration (pydantic-settings).

Env vars use the ``MARKETLENS_`` prefix and ``__`` nesting delimiter, e.g.::

    MARKETLENS_DB__HOST=db
    MARKETLENS_LLM__PROVIDER=anthropic
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class DBConfig(BaseModel):
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    name: str = "marketlens"
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True

    @property
    def dsn(self) -> str:
        """Async SQLAlchemy DSN (asyncpg driver)."""
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class LLMConfig(BaseModel):
    # "ollama" → free, local, offline (default).  "anthropic" → Claude via API key.
    provider: Literal["ollama", "anthropic"] = "ollama"
    ollama_model: str = "qwen2.5"
    ollama_base_url: str = "http://localhost:11434"
    anthropic_model: str = "claude-sonnet-4-5"
    temperature: float = 0.2
    max_tokens: int = 2048

    @property
    def litellm_model(self) -> str:
        """The LiteLLM model string ADK's LiteLlm wrapper expects."""
        if self.provider == "anthropic":
            return f"anthropic/{self.anthropic_model}"
        return f"ollama_chat/{self.ollama_model}"


class EmbeddingConfig(BaseModel):
    model: str = "BAAI/bge-small-en-v1.5"
    dim: int = 384


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MARKETLENS_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db: DBConfig = Field(default_factory=DBConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)

    sec_user_agent: str = "MarketLens demo set-your-email@example.com"
    # NoDecode: let the validator parse comma-separated env values instead of JSON.
    ticker_universe: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["NVDA", "AAPL", "MSFT", "AMZN", "TSLA"]
    )
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    app_name: str = "marketlens"

    @field_validator("ticker_universe", "cors_origins", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("ticker_universe", mode="after")
    @classmethod
    def _upper_tickers(cls, value: list[str]) -> list[str]:
        return [t.upper() for t in value]


@lru_cache
def get_settings() -> Settings:
    return Settings()
