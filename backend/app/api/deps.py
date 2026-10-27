from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, NotFoundError, UnauthorizedError
from app.core.security import InvalidTokenError, TokenType, decode_token
from app.integrations.payments.base import PaymentProvider
from app.integrations.payments.factory import get_payment_provider
from app.models import ClientProfile, TrainerProfile, User, UserRole

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_v1_prefix}/auth/token",
    auto_error=False,
)

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    if not token:
        raise UnauthorizedError("Требуется авторизация")

    try:
        payload = decode_token(token)
    except InvalidTokenError as exc:
        raise UnauthorizedError("Недействительный или просроченный токен") from exc

    if payload.get("type") != TokenType.ACCESS.value:
        raise UnauthorizedError("Ожидался access-токен")

    try:
        user_id = uuid.UUID(str(payload.get("sub")))
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Некорректный токен") from exc

    user = await db.get(User, user_id)
    if user is None:
        raise UnauthorizedError("Пользователь не найден")
    if not user.is_active:
        raise ForbiddenError("Учётная запись заблокирована")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    async def dependency(current_user: CurrentUser) -> User:
        if current_user.role not in roles:
            raise ForbiddenError("Недостаточно прав для выполнения операции")
        return current_user

    return dependency


AdminUser = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
StaffUser = Annotated[
    User,
    Depends(require_roles(UserRole.ADMIN, UserRole.TRAINER)),
]
ClientUser = Annotated[User, Depends(require_roles(UserRole.CLIENT))]


async def get_current_client(
    current_user: ClientUser,
    db: DbSession,
) -> ClientProfile:
    client = await db.scalar(
        select(ClientProfile)
        .where(ClientProfile.user_id == current_user.id)
        .options(joinedload(ClientProfile.user))
    )
    if client is None:
        raise NotFoundError("Профиль клиента не найден")
    return client


async def get_current_trainer(
    current_user: StaffUser,
    db: DbSession,
) -> TrainerProfile:
    if current_user.role == UserRole.ADMIN:
        raise ForbiddenError("Действие доступно только тренеру")
    trainer = await db.scalar(
        select(TrainerProfile)
        .where(TrainerProfile.user_id == current_user.id)
        .options(joinedload(TrainerProfile.user))
    )
    if trainer is None:
        raise NotFoundError("Профиль тренера не найден")
    return trainer


CurrentClient = Annotated[ClientProfile, Depends(get_current_client)]
CurrentTrainer = Annotated[TrainerProfile, Depends(get_current_trainer)]
PaymentProviderDep = Annotated[PaymentProvider, Depends(get_payment_provider)]
