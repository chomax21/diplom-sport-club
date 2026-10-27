from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import NotFoundError
from app.core.pagination import paginate
from app.models import TrainerProfile, User, UserRole
from app.schemas.trainer import TrainerUpdate


def _trainer_loaders():
    return joinedload(TrainerProfile.user)


async def list_trainers(
    db: AsyncSession,
    *,
    search: str | None,
    limit: int,
    offset: int,
) -> tuple[list[TrainerProfile], int]:
    stmt = (
        select(TrainerProfile)
        .join(User, TrainerProfile.user_id == User.id)
        .where(User.role == UserRole.TRAINER)
        .options(_trainer_loaders())
        .order_by(TrainerProfile.created_at.desc())
    )
    if search:
        pattern = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                User.full_name.ilike(pattern),
                User.email.ilike(pattern),
                TrainerProfile.specialization.ilike(pattern),
            )
        )
    return await paginate(db, stmt, limit=limit, offset=offset)


async def get_trainer_or_404(
    db: AsyncSession,
    trainer_id: uuid.UUID,
) -> TrainerProfile:
    trainer = await db.scalar(
        select(TrainerProfile).where(TrainerProfile.id == trainer_id).options(_trainer_loaders())
    )
    if trainer is None:
        raise NotFoundError("Тренер не найден")
    return trainer


async def get_trainer_by_user_id(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> TrainerProfile | None:
    return await db.scalar(
        select(TrainerProfile).where(TrainerProfile.user_id == user_id).options(_trainer_loaders())
    )


async def get_trainer_by_user_id_or_404(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> TrainerProfile:
    trainer = await get_trainer_by_user_id(db, user_id)
    if trainer is None:
        raise NotFoundError("Профиль тренера не найден")
    return trainer


async def update_trainer(
    db: AsyncSession,
    trainer: TrainerProfile,
    payload: TrainerUpdate,
) -> TrainerProfile:
    data = payload.model_dump(exclude_unset=True)

    if data.get("full_name") is not None:
        trainer.user.full_name = data["full_name"].strip()
    if "phone" in data:
        trainer.user.phone = data["phone"]
    for field in ("specialization", "bio"):
        if field in data:
            setattr(trainer, field, data[field])

    await db.commit()
    return await get_trainer_or_404(db, trainer.id)
