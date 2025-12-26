import pytest
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_create_request(client: AsyncClient):
    payload = {
        "title": "Лаба по физике",
        "student_name": "Иванов И.И.",
        "deadline": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "description": "Группа 11-201"
    }

    resp = await client.post("/api/requests", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Лаба по физике"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_create_past_deadline_fails(client: AsyncClient):
    payload = {
        "title": "Просрочка",
        "student_name": "Студент",
        "deadline": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    }

    resp = await client.post("/api/requests", json=payload)
    assert resp.status_code == 400
    assert "Deadline cannot be in the past" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_all_requests(client: AsyncClient):
    # Создаём 2 заявки
    for i in range(2):
        payload = {
            "title": f"Тест {i}",
            "student_name": f"Студент {i}",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        }
        await client.post("/api/requests", json=payload)

    resp = await client.get("/api/requests")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_crud_operations(client: AsyncClient):
    # CREATE
    payload = {
        "title": "CRUD тест",
        "student_name": "Тестер",
        "deadline": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    }
    create_resp = await client.post("/api/requests", json=payload)
    assert create_resp.status_code == 201
    request_id = create_resp.json()["id"]

    # READ
    get_resp = await client.get(f"/api/requests/{request_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == request_id

    # UPDATE
    update_resp = await client.put(f"/api/requests/{request_id}", json={"status": "completed"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "completed"

    # DELETE
    delete_resp = await client.delete(f"/api/requests/{request_id}")
    assert delete_resp.status_code == 204

    # Verify delete
    final_get = await client.get(f"/api/requests/{request_id}")
    assert final_get.status_code == 404
