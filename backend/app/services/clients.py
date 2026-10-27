from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import NotFoundError
from app.core.pagination import paginate
from app.models import ClientProfile, User, UserRole
from app.schemas.client import ClientUpdate


def _client_loaders():
    return joinedload(ClientProfile.user)


async def list_clients(
    db: AsyncSession,
    *,
    search: str | None,
    limit: int,
    offset: int,
) -> tuple[list[ClientProfile], int]:
    stmt = (
        select(ClientProfile)
        .join(User, ClientProfile.user_id == User.id)
        .where(User.role == UserRole.CLIENT)
        .options(_client_loaders())
        .order_by(ClientProfile.created_at.desc())
    )
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                User.full_name.ilike(pattern),
                User.email.ilike(pattern),
                User.phone.ilike(pattern),
            )
        )
    return await paginate(db, stmt, limit=limit, offset=offset)


async def get_client_or_404(db: AsyncSession, client_id: uuid.UUID) -> ClientProfile:
    client = await db.scalar(
        select(ClientProfile).where(ClientProfile.id == client_id).options(_client_loaders())
    )
    if client is None:
        raise NotFoundError("Клиент не найден")
    return client


async def get_client_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> ClientProfile | None:
    return await db.scalar(
        select(ClientProfile).where(ClientProfile.user_id == user_id).options(_client_loaders())
    )


async def get_client_by_user_id_or_404(db: AsyncSession, user_id: uuid.UUID) -> ClientProfile:
    client = await get_client_by_user_id(db, user_id)
    if client is None:
        raise NotFoundError("Профиль клиента не найден")
    return client


async def update_client(
    db: AsyncSession,
    client: ClientProfile,
    payload: ClientUpdate,
) -> ClientProfile:
    data = payload.model_dump(exclude_unset=True)

    if data.get("full_name") is not None:
        client.user.full_name = data["full_name"].strip()
    if "phone" in data:
        client.user.phone = data["phone"]
    for field in ("birth_date", "notes", "emergency_contact"):
        if field in data:
            setattr(client, field, data[field])

    await db.commit()
    await db.refresh(client)
    # После refresh ленивые связи недопустимы — подгружаем user заново.
    return await get_client_or_404(db, client.id)


__all__ = [
    "get_client_by_user_id",
    "get_client_by_user_id_or_404",
    "get_client_or_404",
    "list_clients",
    "update_client",
]
