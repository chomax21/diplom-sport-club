import uuid
from datetime import date

from fastapi import APIRouter

from app.api.deps import AdminUser, DbSession, StaffUser
from app.schemas.report import AttendanceReport, RevenueReport
from app.services import reports as report_service

router = APIRouter(prefix="/reports", tags=["Отчёты"])


@router.get(
    "/attendance",
    response_model=AttendanceReport,
    summary="Отчёт по посещаемости",
)
async def attendance_report(
    db: DbSession,
    current_user: StaffUser,
    date_from: date | None = None,
    date_to: date | None = None,
    trainer_id: uuid.UUID | None = None,
) -> AttendanceReport:
    return await report_service.attendance_report(
        db,
        actor=current_user,
        date_from=date_from,
        date_to=date_to,
        trainer_id=trainer_id,
    )


@router.get(
    "/revenue",
    response_model=RevenueReport,
    summary="Отчёт по выручке (mock-платежи)",
)
async def revenue_report(
    db: DbSession,
    current_user: AdminUser,
    date_from: date | None = None,
    date_to: date | None = None,
) -> RevenueReport:
    return await report_service.revenue_report(
        db,
        actor=current_user,
        date_from=date_from,
        date_to=date_to,
    )
