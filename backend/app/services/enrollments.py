from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.pagination import paginate
from app.core.time import ensure_utc, utcnow
from app.models import (
    Attendance,
    ClientProfile,
    Enrollment,
    EnrollmentStatus,
    Membership,
    MembershipStatus,
    TrainerProfile,
    TrainingSession,
    User,
    UserRole,
)
from app.schemas.training import EnrollmentCreate
from app.services.clients import get_client_by_user_id_or_404, get_client_or_404
from app.services.sessions import get_session_or_404


def _enrollment_options():
    return (
        joinedload(Enrollment.client).joinedload(ClientProfile.user),
        joinedload(Enrollment.attendance),
    )


def _enrollment_full_options():
    return (
        joinedload(Enrollment.client).joinedload(ClientProfile.user),
        joinedload(Enrollment.attendance),
        joinedload(Enrollment.membership),
        joinedload(Enrollment.session)
        .joinedload(TrainingSession.trainer)
        .joinedload(TrainerProfile.user),
    )


async def get_enrollment_or_404(
    db: AsyncSession,
    enrollment_id: uuid.UUID,
) -> Enrollment:
    enrollment = await db.scalar(
        select(Enrollment)
        .where(Enrollment.id == enrollment_id)
        .options(*_enrollment_full_options())
    )
    if enrollment is None:
        raise NotFoundError("Запись на тренировку не найдена")
    return enrollment


def _ensure_trainer_owns_session(enrollment: Enrollment, actor: User) -> None:
    if actor.role == UserRole.ADMIN:
        return
    if actor.role == UserRole.TRAINER and enrollment.session.trainer.user_id == actor.id:
        return
    raise ForbiddenError("Можно отмечать посещение только на своих тренировках")


async def enroll(
    db: AsyncSession,
    session_id: uuid.UUID,
    payload: EnrollmentCreate,
    *,
    actor: User,
) -> Enrollment:
    if actor.role == UserRole.TRAINER:
        raise ForbiddenError("Тренер не может записываться на тренировки")

    if actor.role == UserRole.ADMIN:
        if payload.client_id is None:
            raise ConflictError("Для записи клиента администратором укажите client_id")
        client = await get_client_or_404(db, payload.client_id)
    else:
        client = await get_client_by_user_id_or_404(db, actor.id)
        if payload.client_id is not None and payload.client_id != client.id:
            raise ForbiddenError("Можно записаться только на себя")

    session = await get_session_or_404(db, session_id)
    if session.is_cancelled:
        raise ConflictError("Тренировка отменена")
    if ensure_utc(session.starts_at) <= utcnow():
        raise ConflictError("Запись на тренировку закрыта")

    existing = await db.scalar(
        select(Enrollment).where(
            Enrollment.session_id == session.id,
            Enrollment.client_id == client.id,
        )
    )
    reactivate = False
    if existing is not None:
        if existing.status == EnrollmentStatus.ACTIVE:
            raise ConflictError("Вы уже записаны на эту тренировку")
        if existing.status in (EnrollmentStatus.ATTENDED, EnrollmentStatus.NO_SHOW):
            raise ConflictError("По этой тренировке уже есть отметка посещения")
        reactivate = True

    if session.enrolled_count >= session.capacity:
        raise ConflictError("Свободных мест на тренировке нет")

    session_date = ensure_utc(session.starts_at).date()
    membership = await db.scalar(
        select(Membership)
        .where(
            Membership.client_id == client.id,
            Membership.status == MembershipStatus.ACTIVE,
            Membership.starts_at <= session_date,
            Membership.ends_at >= session_date,
        )
        .order_by(Membership.ends_at.asc())
    )
    if membership is None:
        raise ConflictError("Нет действующего абонемента на дату тренировки. Оформите абонемент.")

    if membership.visits_left is not None:
        booked = await db.scalar(
            select(func.count(Enrollment.id))
            .join(
                TrainingSession,
                Enrollment.session_id == TrainingSession.id,
            )
            .where(
                Enrollment.client_id == client.id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
                TrainingSession.is_cancelled.is_(False),
                TrainingSession.starts_at >= utcnow(),
            )
        )
        if int(booked or 0) >= membership.visits_left:
            raise ConflictError("Недостаточно посещений в абонементе с учётом будущих записей")

    overlap = await db.scalar(
        select(func.count(Enrollment.id))
        .join(
            TrainingSession,
            Enrollment.session_id == TrainingSession.id,
        )
        .where(
            Enrollment.client_id == client.id,
            Enrollment.status == EnrollmentStatus.ACTIVE,
            Enrollment.session_id != session.id,
            TrainingSession.is_cancelled.is_(False),
            TrainingSession.starts_at < session.ends_at,
            TrainingSession.ends_at > session.starts_at,
        )
    )
    if overlap:
        raise ConflictError("У клиента уже есть запись на пересекающуюся тренировку")

    if reactivate and existing is not None:
        existing.status = EnrollmentStatus.ACTIVE
        existing.cancelled_at = None
        existing.membership_id = membership.id
        enrollment = existing
    else:
        enrollment = Enrollment(
            session_id=session.id,
            client_id=client.id,
            membership_id=membership.id,
            status=EnrollmentStatus.ACTIVE,
        )
        db.add(enrollment)

    await db.commit()
    return await get_enrollment_or_404(db, enrollment.id)


async def cancel_enrollment(
    db: AsyncSession,
    enrollment: Enrollment,
    *,
    actor: User,
) -> Enrollment:
    if (
        actor.role == UserRole.ADMIN
        or actor.role == UserRole.CLIENT
        and enrollment.client.user_id == actor.id
    ):
        pass
    else:
        raise ForbiddenError("Можно отменить только свою запись")

    if enrollment.status != EnrollmentStatus.ACTIVE:
        raise ConflictError("Отменить можно только активную запись")
    if enrollment.session.is_cancelled:
        raise ConflictError("Тренировка уже отменена")
    if ensure_utc(enrollment.session.starts_at) <= utcnow():
        raise ConflictError("Нельзя отменить запись после начала тренировки")

    enrollment.status = EnrollmentStatus.CANCELLED
    enrollment.cancelled_at = utcnow()
    await db.commit()
    return await get_enrollment_or_404(db, enrollment.id)


async def list_session_enrollments(
    db: AsyncSession,
    session_id: uuid.UUID,
    *,
    actor: User,
    include_cancelled: bool,
    limit: int,
    offset: int,
) -> tuple[list[Enrollment], int]:
    session = await get_session_or_404(db, session_id)
    if actor.role == UserRole.TRAINER and session.trainer.user_id != actor.id:
        raise ForbiddenError("Можно просматривать только свои тренировки")
    if actor.role not in (UserRole.ADMIN, UserRole.TRAINER):
        raise ForbiddenError("Недостаточно прав")

    stmt = select(Enrollment).where(Enrollment.session_id == session.id)
    if not include_cancelled:
        stmt = stmt.where(Enrollment.status != EnrollmentStatus.CANCELLED)
    stmt = stmt.options(*_enrollment_options()).order_by(Enrollment.created_at.asc())
    return await paginate(db, stmt, limit=limit, offset=offset)


async def my_enrollments(
    db: AsyncSession,
    *,
    actor: User,
    only_upcoming: bool,
    limit: int,
    offset: int,
) -> tuple[list[Enrollment], int]:
    if actor.role != UserRole.CLIENT:
        raise ForbiddenError("Раздел доступен только клиентам")
    client = await get_client_by_user_id_or_404(db, actor.id)

    stmt = select(Enrollment).where(Enrollment.client_id == client.id)
    if only_upcoming:
        stmt = stmt.join(
            TrainingSession,
            Enrollment.session_id == TrainingSession.id,
        ).where(
            Enrollment.status == EnrollmentStatus.ACTIVE,
            TrainingSession.is_cancelled.is_(False),
            TrainingSession.starts_at >= utcnow(),
        )
    stmt = stmt.options(*_enrollment_options()).order_by(Enrollment.created_at.desc())
    return await paginate(db, stmt, limit=limit, offset=offset)


async def mark_attendance(
    db: AsyncSession,
    enrollment: Enrollment,
    *,
    actor: User,
    note: str | None,
) -> Enrollment:
    _ensure_trainer_owns_session(enrollment, actor)

    if enrollment.status != EnrollmentStatus.ACTIVE:
        raise ConflictError("Посещение можно отметить только для активной записи")
    if enrollment.session.is_cancelled:
        raise ConflictError("Тренировка отменена")

    membership = enrollment.membership
    if membership is None:
        raise ConflictError("Не найден абонемент, по которому оформлена запись")

    session_date = ensure_utc(enrollment.session.starts_at).date()
    if membership.status != MembershipStatus.ACTIVE:
        raise ConflictError("Абонемент неактивен")
    if not (membership.starts_at <= session_date <= membership.ends_at):
        raise ConflictError("Абонемент не действует на дату тренировки")
    if membership.visits_left is not None:
        if membership.visits_left <= 0:
            raise ConflictError("В абонементе закончились посещения")
        membership.visits_left -= 1

    enrollment.attendance = Attendance(
        enrollment_id=enrollment.id,
        marked_by_id=actor.id,
        marked_at=utcnow(),
        note=note,
    )
    enrollment.status = EnrollmentStatus.ATTENDED
    await db.commit()
    return await get_enrollment_or_404(db, enrollment.id)


async def mark_no_show(
    db: AsyncSession,
    enrollment: Enrollment,
    *,
    actor: User,
) -> Enrollment:
    _ensure_trainer_owns_session(enrollment, actor)
    if enrollment.status != EnrollmentStatus.ACTIVE:
        raise ConflictError("Отметить неявку можно только для активной записи")
    if enrollment.session.is_cancelled:
        raise ConflictError("Тренировка отменена")

    enrollment.status = EnrollmentStatus.NO_SHOW
    await db.commit()
    return await get_enrollment_or_404(db, enrollment.id)
