from httpx import AsyncClient


async def test_register_login_refresh_and_me(client: AsyncClient) -> None:
    payload = {
        "email": "new.client@example.com",
        "password": "Client12345",
        "full_name": "Новый Клиент",
        "phone": "+7 900 000-00-01",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    created = response.json()
    assert created["email"] == payload["email"]
    assert created["role"] == "client"

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert response.status_code == 200, response.text
    tokens = response.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == payload["full_name"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_duplicate_registration_returns_conflict(client: AsyncClient) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "Client12345",
        "full_name": "Дубликат",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201
    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


async def test_wrong_password_returns_unauthorized(
    client: AsyncClient,
    client_user,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": client_user.email, "password": "WrongPassword123"},
    )
    assert response.status_code == 401


async def test_client_cannot_manage_rooms(
    client: AsyncClient,
    client_token: str,
    auth_headers,
) -> None:
    response = await client.post(
        "/api/v1/rooms",
        json={"name": "Чужой зал", "capacity": 10},
        headers=auth_headers(client_token),
    )
    assert response.status_code == 403
