import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import (
    AdminUser,
    CurrentTrainer,
    CurrentUser,
    DbSession,
)
from app.schemas.common import Page
from app.schemas.trainer import TrainerRead, TrainerUpdate
from app.services import trainers as trainer_service

router = APIRouter(prefix="/trainers", tags=["Тренеры"])


@router.get("", response_model=Page[TrainerRead], summary="Список тренеров")
async def list_trainers(
    db: DbSession,
    _: CurrentUser,
    search: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[TrainerRead]:
    items, total = await trainer_service.list_trainers(
        db,
        search=search,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[TrainerRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/me", response_model=TrainerRead, summary="Мой профиль тренера")
async def get_my_profile(current_trainer: CurrentTrainer) -> TrainerRead:
    return TrainerRead.model_validate(current_trainer)


@router.patch("/me", response_model=TrainerRead, summary="Обновить мой профиль")
async def update_my_profile(
    payload: TrainerUpdate,
    db: DbSession,
    current_trainer: CurrentTrainer,
) -> TrainerRead:
    updated = await trainer_service.update_trainer(db, current_trainer, payload)
    return TrainerRead.model_validate(updated)


@router.get("/{trainer_id}", response_model=TrainerRead, summary="Тренер по ID")
async def get_trainer(
    trainer_id: uuid.UUID,
    db: DbSession,
    _: CurrentUser,
) -> TrainerRead:
    trainer = await trainer_service.get_trainer_or_404(db, trainer_id)
    return TrainerRead.model_validate(trainer)


@router.patch("/{trainer_id}", response_model=TrainerRead, summary="Изменить тренера")
async def update_trainer(
    trainer_id: uuid.UUID,
    payload: TrainerUpdate,
    db: DbSession,
    _: AdminUser,
) -> TrainerRead:
    trainer = await trainer_service.get_trainer_or_404(db, trainer_id)
    updated = await trainer_service.update_trainer(db, trainer, payload)
    return TrainerRead.model_validate(updated)
