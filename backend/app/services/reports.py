from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError
from app.core.time import day_end, day_start, utcnow
from app.models import (
    Enrollment,
    EnrollmentStatus,
    Membership,
    MembershipType,
    Payment,
    PaymentStatus,
    TrainingSession,
    User,
    UserRole,
)
from app.schemas.report import (
    AttendanceReport,
    DailyAttendance,
    DailyRevenue,
    RevenueByMembershipType,
    RevenueReport,
)
from app.services.trainers import get_trainer_by_user_id_or_404


def _as_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _money(value) -> Decimal:
    if value is None:
        return Decimal("0.00")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _resolve_period(date_from: date | None, date_to: date | None) -> tuple[date, date]:
    today = utcnow().date()
    start_date = date_from or (today - timedelta(days=29))
    end_date = date_to or today
    if start_date > end_date:
        raise ConflictError("date_from не может быть позже date_to")
    return start_date, end_date


async def attendance_report(
    db: AsyncSession,
    *,
    actor: User,
    date_from: date | None,
    date_to: date | None,
    trainer_id,
) -> AttendanceReport:
    if actor.role == UserRole.TRAINER:
        trainer = await get_trainer_by_user_id_or_404(db, actor.id)
        if trainer_id is not None and trainer_id != trainer.id:
            raise ForbiddenError("Тренер может смотреть только свою статистику")
        trainer_id = trainer.id
    elif actor.role != UserRole.ADMIN:
        raise ForbiddenError("Недостаточно прав")

    start_date, end_date = _resolve_period(date_from, date_to)
    period_start = day_start(start_date)
    period_end = day_end(end_date)

    session_filters = [
        TrainingSession.starts_at >= period_start,
        TrainingSession.starts_at <= period_end,
        TrainingSession.is_cancelled.is_(False),
    ]
    if trainer_id is not None:
        session_filters.append(TrainingSession.trainer_id == trainer_id)

    enrollment_filters = [
        *session_filters,
        Enrollment.status != EnrollmentStatus.CANCELLED,
    ]

    sessions_count = await db.scalar(select(func.count(TrainingSession.id)).where(*session_filters))

    stats = (
        await db.execute(
            select(
                func.count(Enrollment.id),
                func.coalesce(
                    func.sum(case((Enrollment.status == EnrollmentStatus.ATTENDED, 1), else_=0)),
                    0,
                ),
                func.coalesce(
                    func.sum(case((Enrollment.status == EnrollmentStatus.NO_SHOW, 1), else_=0)),
                    0,
                ),
            )
            .select_from(Enrollment)
            .join(TrainingSession, Enrollment.session_id == TrainingSession.id)
            .where(*enrollment_filters)
        )
    ).one()
    enrollments_count, attended_count, no_show_count = (int(stats[0]), int(stats[1]), int(stats[2]))
    completed = attended_count + no_show_count
    attendance_rate = round(attended_count / completed * 100, 1) if completed else 0.0

    day_expr = func.date(TrainingSession.starts_at)
    day_rows = (
        await db.execute(
            select(
                day_expr.label("day"),
                func.count(Enrollment.id).label("enrollments"),
                func.coalesce(
                    func.sum(case((Enrollment.status == EnrollmentStatus.ATTENDED, 1), else_=0)),
                    0,
                ).label("attended"),
            )
            .select_from(TrainingSession)
            .outerjoin(
                Enrollment,
                and_(
                    Enrollment.session_id == TrainingSession.id,
                    Enrollment.status != EnrollmentStatus.CANCELLED,
                ),
            )
            .where(*session_filters)
            .group_by(day_expr)
            .order_by(day_expr)
        )
    ).all()

    return AttendanceReport(
        date_from=start_date,
        date_to=end_date,
        sessions_count=int(sessions_count or 0),
        enrollments_count=enrollments_count,
        attended_count=attended_count,
        no_show_count=no_show_count,
        attendance_rate=attendance_rate,
        by_day=[
            DailyAttendance(
                day=_as_date(row.day),
                enrollments=int(row.enrollments),
                attended=int(row.attended),
            )
            for row in day_rows
        ],
    )


async def revenue_report(
    db: AsyncSession,
    *,
    actor: User,
    date_from: date | None,
    date_to: date | None,
) -> RevenueReport:
    if actor.role != UserRole.ADMIN:
        raise ForbiddenError("Доступ к финансовой отчётности есть только у администратора")

    start_date, end_date = _resolve_period(date_from, date_to)
    period_start = day_start(start_date)
    period_end = day_end(end_date)

    succeeded_filters = [
        Payment.status == PaymentStatus.SUCCEEDED,
        Payment.paid_at.is_not(None),
        Payment.paid_at >= period_start,
        Payment.paid_at <= period_end,
    ]

    totals = (
        await db.execute(
            select(
                func.count(Payment.id),
                func.coalesce(func.sum(Payment.amount), 0),
            ).where(*succeeded_filters)
        )
    ).one()
    payments_count = int(totals[0])
    total_amount = _money(totals[1])

    refunded_amount = await db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == PaymentStatus.REFUNDED,
            Payment.refunded_at.is_not(None),
            Payment.refunded_at >= period_start,
            Payment.refunded_at <= period_end,
        )
    )

    type_rows = (
        await db.execute(
            select(
                MembershipType.name,
                func.count(Payment.id),
                func.coalesce(func.sum(Payment.amount), 0),
            )
            .select_from(Payment)
            .join(Membership, Payment.membership_id == Membership.id)
            .join(MembershipType, Membership.membership_type_id == MembershipType.id)
            .where(*succeeded_filters)
            .group_by(MembershipType.name)
            .order_by(func.sum(Payment.amount).desc())
        )
    ).all()

    day_expr = func.date(Payment.paid_at)
    day_rows = (
        await db.execute(
            select(
                day_expr.label("day"),
                func.count(Payment.id).label("payments_count"),
                func.coalesce(func.sum(Payment.amount), 0).label("amount"),
            )
            .where(*succeeded_filters)
            .group_by(day_expr)
            .order_by(day_expr)
        )
    ).all()

    return RevenueReport(
        date_from=start_date,
        date_to=end_date,
        payments_count=payments_count,
        total_amount=total_amount,
        refunded_amount=_money(refunded_amount),
        by_membership_type=[
            RevenueByMembershipType(
                membership_type_name=row[0],
                payments_count=int(row[1]),
                amount=_money(row[2]),
            )
            for row in type_rows
        ],
        by_day=[
            DailyRevenue(
                day=_as_date(row.day),
                payments_count=int(row.payments_count),
                amount=_money(row.amount),
            )
            for row in day_rows
        ],
    )
