"""
Basic configuration for the Smart Campus Assistant backend.

For the MVP we keep configuration simple and environment-variable driven,
so it's easy to point to Postgres later (or start with SQLite locally).
"""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Smart Campus Assistant"
    api_prefix: str = "/api"
    environment: str = Field("development", description="Environment name")

    # Database URL – default to local SQLite for quick start.
    # You can replace this with a Postgres URL later, e.g.:
    # postgresql+psycopg://user:password@localhost:5432/smart_campus
    database_url: str = Field(
        "sqlite+aiosqlite:///./smart_campus.db",
        description="SQLAlchemy-compatible database URL",
    )

    # CORS
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Frontend origins allowed to call this API.",
    )

    # RAG / embedding related
    embedding_model_name: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence-transformers model used for embeddings.",
    )
    embedding_cache_dir: str = Field(
        "./.cache/embeddings", description="Local cache dir for models and indexes."
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


