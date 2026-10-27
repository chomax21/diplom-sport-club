import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AdminUser, DbSession
from app.core.exceptions import ConflictError
from app.models.enums import UserRole
from app.schemas.common import Page
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import users as user_service

router = APIRouter(prefix="/users", tags=["Пользователи"])


@router.get("", response_model=Page[UserRead], summary="Список пользователей")
async def list_users(
    db: DbSession,
    _: AdminUser,
    role: UserRole | None = None,
    search: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[UserRead]:
    items, total = await user_service.list_users(
        db,
        role=role,
        search=search,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[UserRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=UserRead, status_code=201, summary="Создать пользователя")
async def create_user(
    payload: UserCreate,
    db: DbSession,
    _: AdminUser,
) -> UserRead:
    user = await user_service.create_user(db, payload)
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead, summary="Пользователь по ID")
async def get_user(
    user_id: uuid.UUID,
    db: DbSession,
    _: AdminUser,
) -> UserRead:
    user = await user_service.get_user_or_404(db, user_id)
    return UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=UserRead, summary="Изменить пользователя")
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    db: DbSession,
    _: AdminUser,
) -> UserRead:
    user = await user_service.get_user_or_404(db, user_id)
    updated = await user_service.update_user(db, user, payload)
    return UserRead.model_validate(updated)


@router.delete(
    "/{user_id}",
    response_model=UserRead,
    summary="Заблокировать пользователя",
)
async def deactivate_user(
    user_id: uuid.UUID,
    db: DbSession,
    current_user: AdminUser,
) -> UserRead:
    if user_id == current_user.id:
        raise ConflictError("Нельзя заблокировать собственную учётную запись")
    user = await user_service.get_user_or_404(db, user_id)
    updated = await user_service.deactivate_user(db, user)
    return UserRead.model_validate(updated)
