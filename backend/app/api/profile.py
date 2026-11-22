"""CRUD endpoints for the single local candidate profile."""

from datetime import timezone, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import UserProfile, UserProfileRead, UserProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])
PROFILE_ID = 1


@router.get("", response_model=UserProfileRead)
async def read_profile(session: AsyncSession = Depends(get_session)) -> UserProfile:
    profile = await session.get(UserProfile, PROFILE_ID)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("", response_model=UserProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    payload: UserProfileUpdate, session: AsyncSession = Depends(get_session)
) -> UserProfile:
    if await session.get(UserProfile, PROFILE_ID):
        raise HTTPException(status_code=409, detail="Profile already exists")
    profile = UserProfile(id=PROFILE_ID, **payload.model_dump())
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.put("", response_model=UserProfileRead)
async def upsert_profile(
    payload: UserProfileUpdate, session: AsyncSession = Depends(get_session)
) -> UserProfile:
    profile = await session.get(UserProfile, PROFILE_ID)
    if profile is None:
        profile = UserProfile(id=PROFILE_ID, **payload.model_dump())
        session.add(profile)
    else:
        for field, value in payload.model_dump().items():
            setattr(profile, field, value)
        profile.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(session: AsyncSession = Depends(get_session)) -> Response:
    profile = await session.get(UserProfile, PROFILE_ID)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    await session.delete(profile)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
