"""Async SQLite engine and session dependency."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from app.config import get_settings

settings = get_settings()
if settings.resolved_database_url.startswith("sqlite"):
    settings.data_dir.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(settings.resolved_database_url, echo=False)
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def create_db_and_tables() -> None:
    """Create tables for a fresh local installation."""
    # Import registers all SQLModel table classes in metadata.
    from app import models  # noqa: F401

    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield one database session per request."""
    async with async_session_factory() as session:
        yield session
