import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.core.exceptions import NotFoundError
from app.models.enums import UserRole
from app.schemas.common import Page
from app.schemas.room import RoomCreate, RoomRead, RoomUpdate
from app.services import rooms as room_service

router = APIRouter(prefix="/rooms", tags=["Залы"])


@router.get("", response_model=Page[RoomRead], summary="Список залов")
async def list_rooms(
    db: DbSession,
    current_user: CurrentUser,
    include_inactive: bool = False,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[RoomRead]:
    effective_include_inactive = include_inactive and current_user.role == UserRole.ADMIN
    items, total = await room_service.list_rooms(
        db,
        include_inactive=effective_include_inactive,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[RoomRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=RoomRead, status_code=201, summary="Создать зал")
async def create_room(
    payload: RoomCreate,
    db: DbSession,
    _: AdminUser,
) -> RoomRead:
    room = await room_service.create_room(db, payload)
    return RoomRead.model_validate(room)


@router.get("/{room_id}", response_model=RoomRead, summary="Зал по ID")
async def get_room(
    room_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> RoomRead:
    room = await room_service.get_room_or_404(db, room_id)
    if not room.is_active and current_user.role != UserRole.ADMIN:
        raise NotFoundError("Зал не найден")
    return RoomRead.model_validate(room)


@router.patch("/{room_id}", response_model=RoomRead, summary="Изменить зал")
async def update_room(
    room_id: uuid.UUID,
    payload: RoomUpdate,
    db: DbSession,
    _: AdminUser,
) -> RoomRead:
    room = await room_service.get_room_or_404(db, room_id)
    updated = await room_service.update_room(db, room, payload)
    return RoomRead.model_validate(updated)


@router.delete("/{room_id}", response_model=RoomRead, summary="Отключить зал")
async def deactivate_room(
    room_id: uuid.UUID,
    db: DbSession,
    _: AdminUser,
) -> RoomRead:
    room = await room_service.get_room_or_404(db, room_id)
    updated = await room_service.deactivate_room(db, room)
    return RoomRead.model_validate(updated)
