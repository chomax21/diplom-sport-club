import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession, StaffUser
from app.schemas.common import Page
from app.schemas.training import AttendanceMark, EnrollmentRead
from app.services import enrollments as enrollment_service

router = APIRouter(prefix="/enrollments", tags=["Записи и посещаемость"])


@router.get("/my", response_model=Page[EnrollmentRead], summary="Мои записи")
async def my_enrollments(
    db: DbSession,
    current_user: CurrentUser,
    only_upcoming: bool = False,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[EnrollmentRead]:
    items, total = await enrollment_service.my_enrollments(
        db,
        actor=current_user,
        only_upcoming=only_upcoming,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[EnrollmentRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete(
    "/{enrollment_id}",
    response_model=EnrollmentRead,
    summary="Отменить запись",
)
async def cancel_enrollment(
    enrollment_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> EnrollmentRead:
    enrollment = await enrollment_service.get_enrollment_or_404(db, enrollment_id)
    updated = await enrollment_service.cancel_enrollment(db, enrollment, actor=current_user)
    return EnrollmentRead.model_validate(updated)


@router.post(
    "/{enrollment_id}/attend",
    response_model=EnrollmentRead,
    summary="Отметить посещение",
)
async def mark_attendance(
    enrollment_id: uuid.UUID,
    db: DbSession,
    current_user: StaffUser,
    payload: AttendanceMark | None = None,
) -> EnrollmentRead:
    enrollment = await enrollment_service.get_enrollment_or_404(db, enrollment_id)
    updated = await enrollment_service.mark_attendance(
        db,
        enrollment,
        actor=current_user,
        note=payload.note if payload else None,
    )
    return EnrollmentRead.model_validate(updated)


@router.post(
    "/{enrollment_id}/no-show",
    response_model=EnrollmentRead,
    summary="Отметить неявку",
)
async def mark_no_show(
    enrollment_id: uuid.UUID,
    db: DbSession,
    current_user: StaffUser,
) -> EnrollmentRead:
    enrollment = await enrollment_service.get_enrollment_or_404(db, enrollment_id)
    updated = await enrollment_service.mark_no_show(db, enrollment, actor=current_user)
    return EnrollmentRead.model_validate(updated)
