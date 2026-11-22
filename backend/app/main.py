"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import create_db_and_tables, engine
from app.api import profile, settings as settings_api, sources, vacancies

settings = get_settings()
scheduler = AsyncIOScheduler(timezone="UTC")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await create_db_and_tables()
    if settings.scheduler_enabled:
        scheduler.start()
    try:
        yield
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)
        await engine.dispose()


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(profile.router, prefix=settings.api_prefix)
app.include_router(settings_api.router, prefix=settings.api_prefix)
app.include_router(sources.router, prefix=settings.api_prefix)
app.include_router(vacancies.router, prefix=settings.api_prefix)


@app.get("/api/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
