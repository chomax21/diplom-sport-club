from datetime import UTC, datetime, timedelta

from httpx import AsyncClient


async def test_revenue_report_uses_mock_payments(
    client: AsyncClient,
    admin_token: str,
    auth_headers,
    purchase: dict,
) -> None:
    response = await client.get(
        "/api/v1/reports/revenue",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    report = response.json()
    assert report["payments_count"] == 1
    assert report["total_amount"] == "4500.00"
    assert report["refunded_amount"] == "0.00" or report["refunded_amount"] == "0"
    assert len(report["by_membership_type"]) == 1
    assert report["by_membership_type"][0]["membership_type_name"] == "Месяц (12 посещений)"


async def test_client_cannot_view_revenue(
    client: AsyncClient,
    client_token: str,
    auth_headers,
) -> None:
    response = await client.get(
        "/api/v1/reports/revenue",
        headers=auth_headers(client_token),
    )
    assert response.status_code == 403


async def test_attendance_report(
    client: AsyncClient,
    client_token: str,
    trainer_token: str,
    admin_token: str,
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
    enrollment_id = response.json()["id"]

    response = await client.post(
        f"/api/v1/enrollments/{enrollment_id}/attend",
        json={},
        headers=auth_headers(trainer_token),
    )
    assert response.status_code == 200

    date_to = (datetime.now(UTC) + timedelta(days=2)).date().isoformat()
    response = await client.get(
        f"/api/v1/reports/attendance?date_from=2020-01-01&date_to={date_to}",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    report = response.json()
    assert report["sessions_count"] == 1
    assert report["enrollments_count"] == 1
    assert report["attended_count"] == 1
    assert report["attendance_rate"] == 100.0
    assert len(report["by_day"]) == 1
