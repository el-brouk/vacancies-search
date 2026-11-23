"""CRUD endpoints for job search sources."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import JobSource, JobSourceCreate, JobSourceRead, JobSourceUpdate

router = APIRouter(prefix="/sources", tags=["sources"])


@router.post("", response_model=JobSourceRead, status_code=status.HTTP_201_CREATED)
async def create_source(
    payload: JobSourceCreate, session: AsyncSession = Depends(get_session)
) -> JobSource:
    source = JobSource(**payload.model_dump())
    session.add(source)
    await session.commit()
    await session.refresh(source)
    return source


@router.get("", response_model=list[JobSourceRead])
async def list_sources(session: AsyncSession = Depends(get_session)) -> list[JobSource]:
    result = await session.execute(select(JobSource).order_by(JobSource.id))
    return list(result.scalars().all())


@router.get("/{source_id}", response_model=JobSourceRead)
async def read_source(
    source_id: int, session: AsyncSession = Depends(get_session)
) -> JobSource:
    source = await session.get(JobSource, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.put("/{source_id}", response_model=JobSourceRead)
async def update_source(
    source_id: int,
    payload: JobSourceUpdate,
    session: AsyncSession = Depends(get_session),
) -> JobSource:
    source = await session.get(JobSource, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    for field, value in payload.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(source, field, value)
    await session.commit()
    await session.refresh(source)
    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int, session: AsyncSession = Depends(get_session)
) -> Response:
    source = await session.get(JobSource, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    await session.delete(source)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
