import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.enums import UserRole
from app.schemas.common import Page
from app.schemas.membership import (
    MembershipTypeCreate,
    MembershipTypeRead,
    MembershipTypeUpdate,
)
from app.services import membership_types as type_service

router = APIRouter(prefix="/membership-types", tags=["Виды абонементов"])


@router.get("", response_model=Page[MembershipTypeRead], summary="Виды абонементов")
async def list_types(
    db: DbSession,
    current_user: CurrentUser,
    include_inactive: bool = False,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[MembershipTypeRead]:
    effective_include_inactive = include_inactive and current_user.role == UserRole.ADMIN
    items, total = await type_service.list_membership_types(
        db,
        include_inactive=effective_include_inactive,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[MembershipTypeRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=MembershipTypeRead,
    status_code=201,
    summary="Создать вид абонемента",
)
async def create_type(
    payload: MembershipTypeCreate,
    db: DbSession,
    _: AdminUser,
) -> MembershipTypeRead:
    membership_type = await type_service.create_membership_type(db, payload)
    return MembershipTypeRead.model_validate(membership_type)


@router.get("/{type_id}", response_model=MembershipTypeRead, summary="Вид абонемента")
async def get_type(
    type_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> MembershipTypeRead:
    membership_type = await type_service.get_membership_type_or_404(db, type_id)
    if not membership_type.is_active and current_user.role != UserRole.ADMIN:
        raise NotFoundError("Вид абонемента не найден")
    return MembershipTypeRead.model_validate(membership_type)


@router.patch("/{type_id}", response_model=MembershipTypeRead, summary="Изменить вид")
async def update_type(
    type_id: uuid.UUID,
    payload: MembershipTypeUpdate,
    db: DbSession,
    _: AdminUser,
) -> MembershipTypeRead:
    membership_type = await type_service.get_membership_type_or_404(db, type_id)
    updated = await type_service.update_membership_type(db, membership_type, payload)
    return MembershipTypeRead.model_validate(updated)


@router.delete("/{type_id}", response_model=MembershipTypeRead, summary="Отключить вид")
async def deactivate_type(
    type_id: uuid.UUID,
    db: DbSession,
    _: AdminUser,
) -> MembershipTypeRead:
    membership_type = await type_service.get_membership_type_or_404(db, type_id)
    updated = await type_service.deactivate_membership_type(db, membership_type)
    return MembershipTypeRead.model_validate(updated)
