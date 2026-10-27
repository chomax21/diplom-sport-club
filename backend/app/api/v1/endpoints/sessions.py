import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession, StaffUser
from app.schemas.common import Page
from app.schemas.training import (
    EnrollmentCreate,
    EnrollmentRead,
    TrainingSessionCreate,
    TrainingSessionRead,
    TrainingSessionUpdate,
)
from app.services import enrollments as enrollment_service
from app.services import sessions as session_service

router = APIRouter(prefix="/sessions", tags=["Расписание тренировок"])


@router.get("", response_model=Page[TrainingSessionRead], summary="Расписание")
async def list_sessions(
    db: DbSession,
    current_user: CurrentUser,
    date_from: date | None = None,
    date_to: date | None = None,
    trainer_id: uuid.UUID | None = None,
    room_id: uuid.UUID | None = None,
    include_cancelled: bool = False,
    search: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[TrainingSessionRead]:
    items, total = await session_service.list_sessions(
        db,
        actor=current_user,
        date_from=date_from,
        date_to=date_to,
        trainer_id=trainer_id,
        room_id=room_id,
        include_cancelled=include_cancelled,
        search=search,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[TrainingSessionRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=TrainingSessionRead,
    status_code=201,
    summary="Создать тренировку",
)
async def create_session(
    payload: TrainingSessionCreate,
    db: DbSession,
    current_user: StaffUser,
) -> TrainingSessionRead:
    session = await session_service.create_session(db, payload, actor=current_user)
    return TrainingSessionRead.model_validate(session)


@router.get(
    "/{session_id}",
    response_model=TrainingSessionRead,
    summary="Тренировка по ID",
)
async def get_session(
    session_id: uuid.UUID,
    db: DbSession,
    _: CurrentUser,
) -> TrainingSessionRead:
    session = await session_service.get_session_or_404(db, session_id)
    return TrainingSessionRead.model_validate(session)


@router.patch(
    "/{session_id}",
    response_model=TrainingSessionRead,
    summary="Изменить тренировку",
)
async def update_session(
    session_id: uuid.UUID,
    payload: TrainingSessionUpdate,
    db: DbSession,
    current_user: StaffUser,
) -> TrainingSessionRead:
    session = await session_service.get_session_or_404(db, session_id)
    updated = await session_service.update_session(db, session, payload, actor=current_user)
    return TrainingSessionRead.model_validate(updated)


@router.post(
    "/{session_id}/cancel",
    response_model=TrainingSessionRead,
    summary="Отменить тренировку",
)
async def cancel_session(
    session_id: uuid.UUID,
    db: DbSession,
    current_user: StaffUser,
) -> TrainingSessionRead:
    session = await session_service.get_session_or_404(db, session_id)
    updated = await session_service.cancel_session(db, session, actor=current_user)
    return TrainingSessionRead.model_validate(updated)


@router.get(
    "/{session_id}/enrollments",
    response_model=Page[EnrollmentRead],
    summary="Записи на тренировку",
)
async def list_session_enrollments(
    session_id: uuid.UUID,
    db: DbSession,
    current_user: StaffUser,
    include_cancelled: bool = False,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[EnrollmentRead]:
    items, total = await enrollment_service.list_session_enrollments(
        db,
        session_id,
        actor=current_user,
        include_cancelled=include_cancelled,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[EnrollmentRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/{session_id}/enrollments",
    response_model=EnrollmentRead,
    status_code=201,
    summary="Записаться на тренировку",
)
async def enroll(
    session_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    payload: EnrollmentCreate | None = None,
) -> EnrollmentRead:
    enrollment = await enrollment_service.enroll(
        db,
        session_id,
        payload or EnrollmentCreate(),
        actor=current_user,
    )
    return EnrollmentRead.model_validate(enrollment)
