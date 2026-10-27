import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AdminUser, CurrentClient, DbSession, StaffUser
from app.schemas.client import ClientRead, ClientUpdate
from app.schemas.common import Page
from app.services import clients as client_service

router = APIRouter(prefix="/clients", tags=["Клиенты"])


@router.get("", response_model=Page[ClientRead], summary="Список клиентов")
async def list_clients(
    db: DbSession,
    _: StaffUser,
    search: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[ClientRead]:
    items, total = await client_service.list_clients(
        db,
        search=search,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[ClientRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/me", response_model=ClientRead, summary="Мой профиль клиента")
async def get_my_profile(current_client: CurrentClient) -> ClientRead:
    return ClientRead.model_validate(current_client)


@router.patch("/me", response_model=ClientRead, summary="Обновить мой профиль")
async def update_my_profile(
    payload: ClientUpdate,
    db: DbSession,
    current_client: CurrentClient,
) -> ClientRead:
    updated = await client_service.update_client(db, current_client, payload)
    return ClientRead.model_validate(updated)


@router.get("/{client_id}", response_model=ClientRead, summary="Клиент по ID")
async def get_client(
    client_id: uuid.UUID,
    db: DbSession,
    _: StaffUser,
) -> ClientRead:
    client = await client_service.get_client_or_404(db, client_id)
    return ClientRead.model_validate(client)


@router.patch("/{client_id}", response_model=ClientRead, summary="Изменить клиента")
async def update_client(
    client_id: uuid.UUID,
    payload: ClientUpdate,
    db: DbSession,
    _: AdminUser,
) -> ClientRead:
    client = await client_service.get_client_or_404(db, client_id)
    updated = await client_service.update_client(db, client, payload)
    return ClientRead.model_validate(updated)
