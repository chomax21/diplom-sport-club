from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.security import (
    InvalidTokenError,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import ClientProfile, User, UserRole
from app.schemas.auth import RegisterRequest, TokenPair


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == normalize_email(email)))


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    return await db.get(User, user_id)


async def register_client(db: AsyncSession, payload: RegisterRequest) -> User:
    email = normalize_email(payload.email)
    if await get_user_by_email(db, email):
        raise ConflictError("Пользователь с таким email уже существует")

    user = User(
        email=email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        phone=payload.phone,
        role=UserRole.CLIENT,
    )
    db.add(user)
    try:
        await db.flush()
        db.add(ClientProfile(user_id=user.id))
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictError("Пользователь с таким email уже существует") from exc

    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User:
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Неверный email или пароль")
    if not user.is_active:
        raise ForbiddenError("Учётная запись заблокирована")
    return user


def issue_tokens(user: User) -> TokenPair:
    subject = str(user.id)
    role = user.role.value if isinstance(user.role, UserRole) else str(user.role)
    return TokenPair(
        access_token=create_access_token(subject, role),
        refresh_token=create_refresh_token(subject, role),
        expires_in=settings.access_token_expire_minutes * 60,
    )


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenPair:
    try:
        payload = decode_token(refresh_token)
    except InvalidTokenError as exc:
        raise UnauthorizedError("Недействительный refresh-токен") from exc

    if payload.get("type") != TokenType.REFRESH.value:
        raise UnauthorizedError("Ожидался refresh-токен")

    try:
        user_id = uuid.UUID(str(payload.get("sub")))
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Некорректный refresh-токен") from exc

    user = await get_user_by_id(db, user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Пользователь не найден или заблокирован")
    return issue_tokens(user)
