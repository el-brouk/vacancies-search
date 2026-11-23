"""CRUD endpoints for local LLM settings."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import AppSettings, AppSettingsRead, AppSettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])
SETTINGS_ID = 1


def public_settings(settings: AppSettings) -> AppSettingsRead:
    return AppSettingsRead(
        id=SETTINGS_ID,
        llm_api_key_configured=bool(settings.llm_api_key),
        llm_base_url=settings.llm_base_url,
        llm_model=settings.llm_model,
        updated_at=settings.updated_at,
    )


@router.get("", response_model=AppSettingsRead)
async def read_settings(session: AsyncSession = Depends(get_session)) -> AppSettingsRead:
    settings = await session.get(AppSettings, SETTINGS_ID)
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return public_settings(settings)


@router.post("", response_model=AppSettingsRead, status_code=status.HTTP_201_CREATED)
async def create_settings(
    payload: AppSettingsUpdate, session: AsyncSession = Depends(get_session)
) -> AppSettingsRead:
    if await session.get(AppSettings, SETTINGS_ID):
        raise HTTPException(status_code=409, detail="Settings already exist")
    settings = AppSettings(id=SETTINGS_ID, **payload.model_dump())
    session.add(settings)
    await session.commit()
    await session.refresh(settings)
    return public_settings(settings)


@router.put("", response_model=AppSettingsRead)
async def upsert_settings(
    payload: AppSettingsUpdate, session: AsyncSession = Depends(get_session)
) -> AppSettingsRead:
    settings = await session.get(AppSettings, SETTINGS_ID)
    values = payload.model_dump(exclude_unset=True)
    if settings is None:
        settings = AppSettings(id=SETTINGS_ID, **values)
        session.add(settings)
    else:
        for field, value in values.items():
            setattr(settings, field, value)
        settings.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(settings)
    return public_settings(settings)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_settings(session: AsyncSession = Depends(get_session)) -> Response:
    settings = await session.get(AppSettings, SETTINGS_ID)
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    await session.delete(settings)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
