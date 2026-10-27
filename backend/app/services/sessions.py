from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.core.pagination import paginate
from app.core.time import day_end, day_start, ensure_utc, utcnow
from app.models import (
    EnrollmentStatus,
    TrainerProfile,
    TrainingSession,
    User,
    UserRole,
)
from app.schemas.training import TrainingSessionCreate, TrainingSessionUpdate
from app.services.rooms import get_room_or_404
from app.services.trainers import get_trainer_by_user_id_or_404


def _session_options():
    return (
        joinedload(TrainingSession.trainer).joinedload(TrainerProfile.user),
        joinedload(TrainingSession.room),
        selectinload(TrainingSession.enrollments),
    )


async def get_session_or_404(
    db: AsyncSession,
    session_id: uuid.UUID,
) -> TrainingSession:
    session = await db.scalar(
        select(TrainingSession).where(TrainingSession.id == session_id).options(*_session_options())
    )
    if session is None:
        raise NotFoundError("Тренировка не найдена")
    return session


async def _resolve_trainer(
    db: AsyncSession,
    payload: TrainingSessionCreate | TrainingSessionUpdate,
    actor: User,
) -> TrainerProfile:
    if actor.role == UserRole.ADMIN:
        if payload.trainer_id is None:
            raise ConflictError("Укажите тренера для тренировки")
        trainer = await db.get(TrainerProfile, payload.trainer_id)
        if trainer is None:
            raise NotFoundError("Тренер не найден")
        return trainer

    if actor.role == UserRole.TRAINER:
        trainer = await get_trainer_by_user_id_or_404(db, actor.id)
        if payload.trainer_id is not None and payload.trainer_id != trainer.id:
            raise ForbiddenError("Тренер может создавать тренировки только для себя")
        return trainer

    raise ForbiddenError("Недостаточно прав для управления тренировками")


def _validate_times(starts_at, ends_at) -> tuple:
    starts = ensure_utc(starts_at)
    ends = ensure_utc(ends_at)
    if ends <= starts:
        raise ConflictError("Время окончания должно быть позже времени начала")
    return starts, ends


async def _check_conflicts(
    db: AsyncSession,
    *,
    trainer_id: uuid.UUID,
    room_id: uuid.UUID,
    starts_at,
    ends_at,
    exclude_id: uuid.UUID | None = None,
) -> None:
    def base(stmt):
        stmt = stmt.where(
            TrainingSession.is_cancelled.is_(False),
            TrainingSession.starts_at < ends_at,
            TrainingSession.ends_at > starts_at,
        )
        if exclude_id is not None:
            stmt = stmt.where(TrainingSession.id != exclude_id)
        return stmt

    trainer_conflict = await db.scalar(
        base(select(TrainingSession.id).where(TrainingSession.trainer_id == trainer_id)).limit(1)
    )
    if trainer_conflict:
        raise ConflictError("У тренера уже есть тренировка в это время")

    room_conflict = await db.scalar(
        base(select(TrainingSession.id).where(TrainingSession.room_id == room_id)).limit(1)
    )
    if room_conflict:
        raise ConflictError("Зал уже занят в это время")


def _ensure_can_manage(session: TrainingSession, actor: User) -> None:
    if actor.role == UserRole.ADMIN:
        return
    if actor.role == UserRole.TRAINER and session.trainer.user_id == actor.id:
        return
    raise ForbiddenError("Можно управлять только своими тренировками")


async def create_session(
    db: AsyncSession,
    payload: TrainingSessionCreate,
    *,
    actor: User,
) -> TrainingSession:
    trainer = await _resolve_trainer(db, payload, actor)
    room = await get_room_or_404(db, payload.room_id)
    if not room.is_active:
        raise ConflictError("Зал недоступен")

    starts_at, ends_at = _validate_times(payload.starts_at, payload.ends_at)
    if starts_at <= utcnow():
        raise ConflictError("Нельзя создать тренировку в прошлом")
    if payload.capacity > room.capacity:
        raise ConflictError(
            f"Вместимость тренировки не может превышать вместимость зала ({room.capacity})"
        )

    await _check_conflicts(
        db,
        trainer_id=trainer.id,
        room_id=room.id,
        starts_at=starts_at,
        ends_at=ends_at,
    )

    session = TrainingSession(
        title=payload.title.strip(),
        trainer_id=trainer.id,
        room_id=room.id,
        starts_at=starts_at,
        ends_at=ends_at,
        capacity=payload.capacity,
        description=payload.description,
    )
    db.add(session)
    await db.commit()
    return await get_session_or_404(db, session.id)


async def update_session(
    db: AsyncSession,
    session: TrainingSession,
    payload: TrainingSessionUpdate,
    *,
    actor: User,
) -> TrainingSession:
    _ensure_can_manage(session, actor)
    data = payload.model_dump(exclude_unset=True)

    trainer_id = session.trainer_id
    if data.get("trainer_id") is not None:
        trainer = await _resolve_trainer(db, payload, actor)
        trainer_id = trainer.id

    room_id = session.room_id
    if data.get("room_id") is not None:
        room = await get_room_or_404(db, data["room_id"])
        if not room.is_active:
            raise ConflictError("Зал недоступен")
        room_id = room.id
    else:
        room = await get_room_or_404(db, session.room_id)

    starts_at = ensure_utc(data.get("starts_at", session.starts_at))
    ends_at = ensure_utc(data.get("ends_at", session.ends_at))
    starts_at, ends_at = _validate_times(starts_at, ends_at)

    capacity = data.get("capacity", session.capacity)
    if capacity > room.capacity:
        raise ConflictError(
            f"Вместимость тренировки не может превышать вместимость зала ({room.capacity})"
        )
    active_enrollments = sum(
        1 for item in session.enrollments if item.status == EnrollmentStatus.ACTIVE
    )
    if capacity < active_enrollments:
        raise ConflictError(
            f"Нельзя уменьшить вместимость ниже числа записанных ({active_enrollments})"
        )

    await _check_conflicts(
        db,
        trainer_id=trainer_id,
        room_id=room_id,
        starts_at=starts_at,
        ends_at=ends_at,
        exclude_id=session.id,
    )

    if data.get("title") is not None:
        session.title = data["title"].strip()
    if "description" in data:
        session.description = data["description"]
    session.trainer_id = trainer_id
    session.room_id = room_id
    session.starts_at = starts_at
    session.ends_at = ends_at
    session.capacity = capacity

    await db.commit()
    return await get_session_or_404(db, session.id)


async def cancel_session(
    db: AsyncSession,
    session: TrainingSession,
    *,
    actor: User,
) -> TrainingSession:
    _ensure_can_manage(session, actor)
    if session.is_cancelled:
        raise ConflictError("Тренировка уже отменена")

    now = utcnow()
    session.is_cancelled = True
    for enrollment in session.enrollments:
        if enrollment.status == EnrollmentStatus.ACTIVE:
            enrollment.status = EnrollmentStatus.CANCELLED
            enrollment.cancelled_at = now

    await db.commit()
    return await get_session_or_404(db, session.id)


async def list_sessions(
    db: AsyncSession,
    *,
    actor: User,
    date_from: date | None,
    date_to: date | None,
    trainer_id: uuid.UUID | None,
    room_id: uuid.UUID | None,
    include_cancelled: bool,
    search: str | None,
    limit: int,
    offset: int,
) -> tuple[list[TrainingSession], int]:
    if date_from is not None and date_to is not None and date_from > date_to:
        raise ConflictError("date_from не может быть позже date_to")

    stmt = select(TrainingSession).options(*_session_options())

    if date_from is not None:
        stmt = stmt.where(TrainingSession.starts_at >= day_start(date_from))
    if date_to is not None:
        stmt = stmt.where(TrainingSession.starts_at <= day_end(date_to))
    if trainer_id is not None:
        stmt = stmt.where(TrainingSession.trainer_id == trainer_id)
    if room_id is not None:
        stmt = stmt.where(TrainingSession.room_id == room_id)
    if search:
        stmt = stmt.where(TrainingSession.title.ilike(f"%{search.strip()}%"))

    # Клиенты не должны видеть отменённые тренировки через фильтр.
    effective_include_cancelled = include_cancelled and actor.role != UserRole.CLIENT
    if not effective_include_cancelled:
        stmt = stmt.where(TrainingSession.is_cancelled.is_(False))

    stmt = stmt.order_by(TrainingSession.starts_at.asc())
    return await paginate(db, stmt, limit=limit, offset=offset)
