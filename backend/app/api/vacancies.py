"""CRUD endpoints for vacancies."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import JobSource, Vacancy, VacancyCreate, VacancyRead, VacancyUpdate

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


async def validate_source(source_id: int | None, session: AsyncSession) -> None:
    if source_id is not None and await session.get(JobSource, source_id) is None:
        raise HTTPException(status_code=404, detail="Source not found")


@router.post("", response_model=VacancyRead, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    payload: VacancyCreate, session: AsyncSession = Depends(get_session)
) -> Vacancy:
    await validate_source(payload.source_id, session)
    vacancy = Vacancy(**payload.model_dump())
    session.add(vacancy)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Vacancy URL already exists") from exc
    await session.refresh(vacancy)
    return vacancy


@router.get("", response_model=list[VacancyRead])
async def list_vacancies(session: AsyncSession = Depends(get_session)) -> list[Vacancy]:
    result = await session.execute(select(Vacancy).order_by(Vacancy.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{vacancy_id}", response_model=VacancyRead)
async def read_vacancy(
    vacancy_id: int, session: AsyncSession = Depends(get_session)
) -> Vacancy:
    vacancy = await session.get(Vacancy, vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return vacancy


@router.put("/{vacancy_id}", response_model=VacancyRead)
async def update_vacancy(
    vacancy_id: int,
    payload: VacancyUpdate,
    session: AsyncSession = Depends(get_session),
) -> Vacancy:
    vacancy = await session.get(Vacancy, vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    changes = payload.model_dump(exclude_unset=True)
    await validate_source(changes.get("source_id", vacancy.source_id), session)
    for field, value in changes.items():
        setattr(vacancy, field, value)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Vacancy URL already exists") from exc
    await session.refresh(vacancy)
    return vacancy


@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy(
    vacancy_id: int, session: AsyncSession = Depends(get_session)
) -> Response:
    vacancy = await session.get(Vacancy, vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    await session.delete(vacancy)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
