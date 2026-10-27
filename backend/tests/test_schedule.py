from datetime import UTC, datetime, timedelta

from httpx import AsyncClient


def _as_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


async def test_session_overlap_is_rejected(
    client: AsyncClient,
    admin_token: str,
    auth_headers,
    training_session: dict,
    room: dict,
) -> None:
    starts_at = _as_datetime(training_session["starts_at"]) + timedelta(minutes=30)
    response = await client.post(
        "/api/v1/sessions",
        json={
            "title": "Пересекающаяся тренировка",
            "trainer_id": training_session["trainer_id"],
            "room_id": room["id"],
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(minutes=60)).isoformat(),
            "capacity": 5,
        },
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 409


async def test_enrollment_attendance_and_visit_deduction(
    client: AsyncClient,
    client_token: str,
    trainer_token: str,
    auth_headers,
    training_session: dict,
    purchase: dict,
) -> None:
    headers = auth_headers(client_token)
    response = await client.post(
        f"/api/v1/sessions/{training_session['id']}/enrollments",
        json={},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    enrollment = response.json()
    assert enrollment["status"] == "active"
    assert enrollment["is_attended"] is False

    duplicate = await client.post(
        f"/api/v1/sessions/{training_session['id']}/enrollments",
        json={},
        headers=headers,
    )
    assert duplicate.status_code == 409

    response = await client.get(
        f"/api/v1/sessions/{training_session['id']}/enrollments",
        headers=auth_headers(trainer_token),
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = await client.post(
        f"/api/v1/enrollments/{enrollment['id']}/attend",
        json={"note": "Был на тренировке"},
        headers=auth_headers(trainer_token),
    )
    assert response.status_code == 200, response.text
    attended = response.json()
    assert attended["status"] == "attended"
    assert attended["is_attended"] is True

    response = await client.get(
        "/api/v1/memberships",
        headers=headers,
    )
    assert response.status_code == 200
    membership = response.json()["items"][0]
    assert membership["visits_left"] == 11


async def test_capacity_limit(
    client: AsyncClient,
    client_token: str,
    admin_token: str,
    auth_headers,
    room: dict,
    trainer_profile,
    purchase: dict,
) -> None:
    starts_at = (datetime.now(UTC) + timedelta(days=2)).replace(
        hour=12, minute=0, second=0, microsecond=0
    )
    response = await client.post(
        "/api/v1/sessions",
        json={
            "title": "Тренировка на одного",
            "trainer_id": str(trainer_profile.id),
            "room_id": room["id"],
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
            "capacity": 1,
        },
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201
    session_id = response.json()["id"]

    first = await client.post(
        f"/api/v1/sessions/{session_id}/enrollments",
        json={},
        headers=auth_headers(client_token),
    )
    assert first.status_code == 201

    registration = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "second.client@example.com",
            "password": "Client12345",
            "full_name": "Второй Клиент",
        },
    )
    assert registration.status_code == 201
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "second.client@example.com", "password": "Client12345"},
    )
    second_token = login.json()["access_token"]

    second = await client.post(
        f"/api/v1/sessions/{session_id}/enrollments",
        json={},
        headers=auth_headers(second_token),
    )
    assert second.status_code == 409


async def test_enrollment_without_membership_is_rejected(
    client: AsyncClient,
    client_token: str,
    auth_headers,
    training_session: dict,
) -> None:
    response = await client.post(
        f"/api/v1/sessions/{training_session['id']}/enrollments",
        json={},
        headers=auth_headers(client_token),
    )
    assert response.status_code == 409
    assert "абонемент" in response.json()["detail"].lower()


async def test_client_cannot_create_session(
    client: AsyncClient,
    client_token: str,
    auth_headers,
    room: dict,
    trainer_profile,
) -> None:
    starts_at = datetime.now(UTC) + timedelta(days=3)
    response = await client.post(
        "/api/v1/sessions",
        json={
            "title": "Чужая тренировка",
            "trainer_id": str(trainer_profile.id),
            "room_id": room["id"],
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(hours=1)).isoformat(),
            "capacity": 5,
        },
        headers=auth_headers(client_token),
    )
    assert response.status_code == 403
