from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.pagination import paginate
from app.models import Room
from app.schemas.room import RoomCreate, RoomUpdate


async def list_rooms(
    db: AsyncSession,
    *,
    include_inactive: bool,
    limit: int,
    offset: int,
) -> tuple[list[Room], int]:
    stmt = select(Room)
    if not include_inactive:
        stmt = stmt.where(Room.is_active.is_(True))
    stmt = stmt.order_by(Room.name.asc())
    return await paginate(db, stmt, limit=limit, offset=offset)


async def get_room_or_404(db: AsyncSession, room_id: uuid.UUID) -> Room:
    room = await db.get(Room, room_id)
    if room is None:
        raise NotFoundError("Зал не найден")
    return room


async def _ensure_name_is_free(
    db: AsyncSession,
    name: str,
    *,
    exclude_id: uuid.UUID | None = None,
) -> None:
    stmt = select(Room.id).where(func.lower(Room.name) == name.strip().lower())
    if exclude_id is not None:
        stmt = stmt.where(Room.id != exclude_id)
    if await db.scalar(stmt):
        raise ConflictError("Зал с таким названием уже существует")


async def create_room(db: AsyncSession, payload: RoomCreate) -> Room:
    await _ensure_name_is_free(db, payload.name)
    room = Room(
        name=payload.name.strip(),
        capacity=payload.capacity,
        description=payload.description,
        is_active=payload.is_active,
    )
    db.add(room)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Зал с таким названием уже существует") from exc
    await db.refresh(room)
    return room


async def update_room(db: AsyncSession, room: Room, payload: RoomUpdate) -> Room:
    data = payload.model_dump(exclude_unset=True)
    if data.get("name") is not None:
        await _ensure_name_is_free(db, data["name"], exclude_id=room.id)
        room.name = data["name"].strip()

    for field in ("capacity", "description", "is_active"):
        if field in data:
            setattr(room, field, data[field])

    await db.commit()
    await db.refresh(room)
    return room


async def deactivate_room(db: AsyncSession, room: Room) -> Room:
    room.is_active = False
    await db.commit()
    await db.refresh(room)
    return room
