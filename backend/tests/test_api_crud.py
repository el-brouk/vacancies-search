"""End-to-end API coverage for profile, settings, sources, and vacancies."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_profile_crud(client: AsyncClient) -> None:
    assert (await client.get("/api/profile")).status_code == 404

    created = await client.post(
        "/api/profile",
        json={
            "resume_text": "Python developer",
            "preferences": "Remote",
            "stop_words": ["intern"],
            "min_match_score": 75,
        },
    )
    assert created.status_code == 201
    assert created.json()["id"] == 1
    assert created.json()["stop_words"] == ["intern"]
    assert (await client.post("/api/profile", json={})).status_code == 409

    updated = await client.put(
        "/api/profile",
        json={
            "resume_text": "Senior Python developer",
            "preferences": "Hybrid",
            "stop_words": [],
            "min_match_score": 80,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["resume_text"] == "Senior Python developer"
    assert (await client.get("/api/profile")).json()["min_match_score"] == 80
    assert (await client.delete("/api/profile")).status_code == 204
    assert (await client.get("/api/profile")).status_code == 404


@pytest.mark.asyncio
async def test_settings_crud_never_returns_api_key(client: AsyncClient) -> None:
    assert (await client.get("/api/settings")).status_code == 404
    created = await client.post(
        "/api/settings",
        json={
            "llm_api_key": "local-test-secret",
            "llm_base_url": "https://example.test/v1",
            "llm_model": "test-model",
        },
    )
    assert created.status_code == 201
    assert created.json()["llm_api_key_configured"] is True
    assert "local-test-secret" not in created.text

    updated = await client.put("/api/settings", json={"llm_model": "updated-model"})
    assert updated.status_code == 200
    assert updated.json()["llm_model"] == "updated-model"
    assert updated.json()["llm_api_key_configured"] is True
    assert (await client.delete("/api/settings")).status_code == 204
    assert (await client.get("/api/settings")).status_code == 404


@pytest.mark.asyncio
async def test_source_crud(client: AsyncClient) -> None:
    created = await client.post(
        "/api/sources", json={"name": "Engineering", "url": "https://jobs.test"}
    )
    assert created.status_code == 201
    source_id = created.json()["id"]
    assert created.json()["check_interval_hours"] == 4
    assert len((await client.get("/api/sources")).json()) == 1
    assert (await client.get(f"/api/sources/{source_id}")).status_code == 200

    updated = await client.put(
        f"/api/sources/{source_id}", json={"name": "Engineering remote", "is_active": False}
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Engineering remote"
    assert updated.json()["is_active"] is False
    assert (await client.delete(f"/api/sources/{source_id}")).status_code == 204
    assert (await client.get(f"/api/sources/{source_id}")).status_code == 404


@pytest.mark.asyncio
async def test_vacancy_crud_and_url_uniqueness(client: AsyncClient) -> None:
    source = await client.post(
        "/api/sources", json={"name": "Engineering", "url": "https://jobs.test"}
    )
    source_id = source.json()["id"]
    vacancy_payload = {
        "source_id": source_id,
        "url": "https://jobs.test/vacancy/1",
        "title": "Backend engineer",
        "company": "Example",
        "match_score": 90,
        "pros_json": ["Python"],
        "cons_json": [],
    }
    created = await client.post("/api/vacancies", json=vacancy_payload)
    assert created.status_code == 201
    vacancy_id = created.json()["id"]
    assert created.json()["status"] == "new"
    assert (await client.post("/api/vacancies", json=vacancy_payload)).status_code == 409
    assert len((await client.get("/api/vacancies")).json()) == 1
    assert (await client.get(f"/api/vacancies/{vacancy_id}")).status_code == 200

    updated = await client.put(
        f"/api/vacancies/{vacancy_id}",
        json={"status": "favorite", "salary": "100-150k", "match_score": 95},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "favorite"
    assert updated.json()["salary"] == "100-150k"
    assert (await client.delete(f"/api/vacancies/{vacancy_id}")).status_code == 204
    assert (await client.get(f"/api/vacancies/{vacancy_id}")).status_code == 404


@pytest.mark.asyncio
async def test_api_validates_score_and_missing_related_source(client: AsyncClient) -> None:
    invalid_score = await client.post(
        "/api/vacancies", json={"url": "https://jobs.test/invalid", "match_score": 101}
    )
    assert invalid_score.status_code == 422

    missing_source = await client.post(
        "/api/vacancies",
        json={"url": "https://jobs.test/missing", "source_id": 999},
    )
    assert missing_source.status_code == 404
