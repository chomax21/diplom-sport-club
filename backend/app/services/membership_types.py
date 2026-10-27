from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.pagination import paginate
from app.models import MembershipType
from app.schemas.membership import MembershipTypeCreate, MembershipTypeUpdate


async def list_membership_types(
    db: AsyncSession,
    *,
    include_inactive: bool,
    limit: int,
    offset: int,
) -> tuple[list[MembershipType], int]:
    stmt = select(MembershipType)
    if not include_inactive:
        stmt = stmt.where(MembershipType.is_active.is_(True))
    stmt = stmt.order_by(MembershipType.price.asc())
    return await paginate(db, stmt, limit=limit, offset=offset)


async def get_membership_type_or_404(
    db: AsyncSession,
    type_id: uuid.UUID,
) -> MembershipType:
    membership_type = await db.get(MembershipType, type_id)
    if membership_type is None:
        raise NotFoundError("Вид абонемента не найден")
    return membership_type


async def _ensure_name_is_free(
    db: AsyncSession,
    name: str,
    *,
    exclude_id: uuid.UUID | None = None,
) -> None:
    stmt = select(MembershipType.id).where(func.lower(MembershipType.name) == name.strip().lower())
    if exclude_id is not None:
        stmt = stmt.where(MembershipType.id != exclude_id)
    if await db.scalar(stmt):
        raise ConflictError("Вид абонемента с таким названием уже существует")


async def create_membership_type(
    db: AsyncSession,
    payload: MembershipTypeCreate,
) -> MembershipType:
    await _ensure_name_is_free(db, payload.name)
    membership_type = MembershipType(
        name=payload.name.strip(),
        description=payload.description,
        price=payload.price,
        duration_days=payload.duration_days,
        visits_limit=payload.visits_limit,
        is_active=payload.is_active,
    )
    db.add(membership_type)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Вид абонемента с таким названием уже существует") from exc
    await db.refresh(membership_type)
    return membership_type


async def update_membership_type(
    db: AsyncSession,
    membership_type: MembershipType,
    payload: MembershipTypeUpdate,
) -> MembershipType:
    data = payload.model_dump(exclude_unset=True)
    if data.get("name") is not None:
        await _ensure_name_is_free(db, data["name"], exclude_id=membership_type.id)
        membership_type.name = data["name"].strip()

    for field in ("description", "price", "duration_days", "visits_limit", "is_active"):
        if field in data:
            setattr(membership_type, field, data[field])

    await db.commit()
    await db.refresh(membership_type)
    return membership_type


async def deactivate_membership_type(
    db: AsyncSession,
    membership_type: MembershipType,
) -> MembershipType:
    membership_type.is_active = False
    await db.commit()
    await db.refresh(membership_type)
    return membership_type
