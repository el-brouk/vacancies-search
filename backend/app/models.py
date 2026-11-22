"""SQLModel tables and API schemas for vacancy search data."""

from datetime import datetime, timezone
from enum import Enum

from pydantic import ConfigDict
from sqlalchemy import JSON
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class VacancyStatus(str, Enum):
    NEW = "new"
    FAVORITE = "favorite"
    APPLIED = "applied"
    REJECTED = "rejected"


class UserProfile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    resume_text: str = ""
    preferences: str = ""
    stop_words: list[str] = Field(default_factory=list, sa_type=JSON, nullable=False)
    min_match_score: int = Field(default=70, ge=0, le=100)
    updated_at: datetime = Field(default_factory=utc_now)


class JobSource(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    url: str = Field(index=True)
    is_active: bool = True
    check_interval_hours: int = Field(default=4, ge=1)
    last_run_at: datetime | None = None
    last_status: str | None = None
    last_error: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class Vacancy(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    source_id: int | None = Field(default=None, foreign_key="jobsource.id", index=True)
    url: str = Field(unique=True, index=True)
    title: str = ""
    company: str = ""
    salary: str | None = None
    raw_text: str = ""
    match_score: int | None = Field(default=None, ge=0, le=100)
    ai_summary: str = ""
    pros_json: list[str] = Field(default_factory=list, sa_type=JSON, nullable=False)
    cons_json: list[str] = Field(default_factory=list, sa_type=JSON, nullable=False)
    is_stop_word_triggered: bool = False
    status: VacancyStatus = Field(default=VacancyStatus.NEW)
    created_at: datetime = Field(default_factory=utc_now, index=True)


class AppSettings(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    updated_at: datetime = Field(default_factory=utc_now)


# Request/response schemas keep write-only secrets out of normal API responses.
class UserProfileRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_text: str
    preferences: str
    stop_words: list[str]
    min_match_score: int
    updated_at: datetime


class UserProfileUpdate(SQLModel):
    resume_text: str = ""
    preferences: str = ""
    stop_words: list[str] = Field(default_factory=list)
    min_match_score: int = Field(default=70, ge=0, le=100)


class JobSourceCreate(SQLModel):
    name: str
    url: str
    is_active: bool = True
    check_interval_hours: int = Field(default=4, ge=1)


class JobSourceUpdate(SQLModel):
    name: str | None = None
    url: str | None = None
    is_active: bool | None = None
    check_interval_hours: int | None = Field(default=None, ge=1)


class JobSourceRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    is_active: bool
    check_interval_hours: int
    last_run_at: datetime | None
    last_status: str | None
    last_error: str | None
    created_at: datetime


class VacancyRead(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_id: int | None
    url: str
    title: str
    company: str
    salary: str | None
    raw_text: str
    match_score: int | None
    ai_summary: str
    pros_json: list[str]
    cons_json: list[str]
    is_stop_word_triggered: bool
    status: VacancyStatus
    created_at: datetime


class VacancyCreate(SQLModel):
    source_id: int | None = None
    url: str
    title: str = ""
    company: str = ""
    salary: str | None = None
    raw_text: str = ""
    match_score: int | None = Field(default=None, ge=0, le=100)
    ai_summary: str = ""
    pros_json: list[str] = Field(default_factory=list)
    cons_json: list[str] = Field(default_factory=list)
    is_stop_word_triggered: bool = False
    status: VacancyStatus = VacancyStatus.NEW


class VacancyUpdate(SQLModel):
    source_id: int | None = None
    url: str | None = None
    title: str | None = None
    company: str | None = None
    salary: str | None = None
    raw_text: str | None = None
    match_score: int | None = Field(default=None, ge=0, le=100)
    ai_summary: str | None = None
    pros_json: list[str] | None = None
    cons_json: list[str] | None = None
    is_stop_word_triggered: bool | None = None
    status: VacancyStatus | None = None


class AppSettingsUpdate(SQLModel):
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"


class AppSettingsRead(SQLModel):
    id: int
    llm_api_key_configured: bool
    llm_base_url: str
    llm_model: str
    updated_at: datetime
