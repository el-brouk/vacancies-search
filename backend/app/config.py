"""Application settings and local data paths."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Environment-backed configuration; user data stays under ``data/``."""

    app_name: str = "Vacancies Search API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    scheduler_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="VACANCIES_",
        extra="ignore",
    )

    @property
    def resolved_database_url(self) -> str:
        database_path = self.data_dir / "vacancies_search.db"
        return f"sqlite+aiosqlite:///{database_path.as_posix()}"

    @property
    def data_dir(self) -> Path:
        """Fixed local directory for all private application data."""
        return PROJECT_ROOT / "data"


@lru_cache
def get_settings() -> Settings:
    return Settings()
