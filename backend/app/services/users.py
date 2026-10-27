from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.pagination import paginate
from app.core.security import hash_password
from app.models import ClientProfile, TrainerProfile, User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth import normalize_email


async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    email = normalize_email(payload.email)
    if await db.scalar(select(User.id).where(User.email == email)):
        raise ConflictError("Пользователь с таким email уже существует")

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        phone=payload.phone,
        role=payload.role,
    )
    db.add(user)
    try:
        await db.flush()
        if payload.role == UserRole.CLIENT:
            db.add(ClientProfile(user_id=user.id))
        elif payload.role == UserRole.TRAINER:
            db.add(TrainerProfile(user_id=user.id))
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Не удалось создать пользователя: email уже занят") from exc

    await db.refresh(user)
    return user


async def list_users(
    db: AsyncSession,
    *,
    role: UserRole | None,
    search: str | None,
    limit: int,
    offset: int,
) -> tuple[list[User], int]:
    stmt = select(User)
    if role is not None:
        stmt = stmt.where(User.role == role)
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                User.full_name.ilike(pattern),
                User.email.ilike(pattern),
                User.phone.ilike(pattern),
            )
        )
    stmt = stmt.order_by(User.created_at.desc())
    return await paginate(db, stmt, limit=limit, offset=offset)


async def get_user_or_404(db: AsyncSession, user_id: uuid.UUID) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise NotFoundError("Пользователь не найден")
    return user


async def update_user(db: AsyncSession, user: User, payload: UserUpdate) -> User:
    data = payload.model_dump(exclude_unset=True)
    if data.get("full_name") is not None:
        user.full_name = data["full_name"].strip()
    if "phone" in data:
        user.phone = data["phone"]
    if data.get("is_active") is not None:
        user.is_active = data["is_active"]

    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(db: AsyncSession, user: User) -> User:
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user


__all__ = [
    "create_user",
    "deactivate_user",
    "get_user_or_404",
    "list_users",
    "update_user",
]
