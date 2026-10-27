import uuid

from httpx import AsyncClient


async def test_mock_purchase_creates_membership_and_payment(
    client: AsyncClient,
    client_token: str,
    admin_token: str,
    auth_headers,
    purchase: dict,
) -> None:
    membership = purchase["membership"]
    payment = purchase["payment"]
    assert membership["status"] == "active"
    assert membership["visits_left"] == 12
    assert membership["membership_type_name"] == "Месяц (12 посещений)"
    assert payment["status"] == "succeeded"
    assert payment["provider"] == "mock"
    assert payment["external_id"].startswith("mock-")
    assert payment["amount"] == "4500.00"

    response = await client.get(
        "/api/v1/memberships",
        headers=auth_headers(client_token),
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1

    response = await client.get(
        "/api/v1/payments",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1


async def test_refund_cancels_membership(
    client: AsyncClient,
    admin_token: str,
    auth_headers,
    purchase: dict,
) -> None:
    payment_id = purchase["payment"]["id"]
    response = await client.post(
        f"/api/v1/payments/{payment_id}/refund",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200, response.text
    refunded = response.json()
    assert refunded["status"] == "refunded"
    assert refunded["refunded_at"] is not None

    response = await client.get(
        f"/api/v1/memberships/{purchase['membership']['id']}",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    assert response.json()["visits_left"] == 0


async def test_client_cannot_buy_membership_for_another_client(
    client: AsyncClient,
    client_token: str,
    auth_headers,
    membership_type: dict,
) -> None:
    response = await client.post(
        "/api/v1/memberships/purchase",
        json={
            "membership_type_id": membership_type["id"],
            "client_id": str(uuid.uuid4()),
        },
        headers=auth_headers(client_token),
    )
    assert response.status_code == 403


async def test_trainer_cannot_buy_membership(
    client: AsyncClient,
    trainer_token: str,
    auth_headers,
    membership_type: dict,
) -> None:
    response = await client.post(
        "/api/v1/memberships/purchase",
        json={"membership_type_id": membership_type["id"]},
        headers=auth_headers(trainer_token),
    )
    assert response.status_code == 403
