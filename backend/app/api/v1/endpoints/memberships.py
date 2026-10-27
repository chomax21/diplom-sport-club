import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import (
    AdminUser,
    CurrentUser,
    DbSession,
    PaymentProviderDep,
)
from app.models.enums import MembershipStatus
from app.schemas.common import Page
from app.schemas.membership import (
    MembershipRead,
    PurchaseRequest,
    PurchaseResponse,
)
from app.services import memberships as membership_service

router = APIRouter(prefix="/memberships", tags=["Абонементы"])


@router.get("", response_model=Page[MembershipRead], summary="Список абонементов")
async def list_memberships(
    db: DbSession,
    current_user: CurrentUser,
    status: MembershipStatus | None = None,
    client_id: uuid.UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[MembershipRead]:
    items, total = await membership_service.list_memberships(
        db,
        actor=current_user,
        status=status,
        client_id=client_id,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[MembershipRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/purchase",
    response_model=PurchaseResponse,
    status_code=201,
    summary="Оформить абонемент",
)
async def purchase_membership(
    payload: PurchaseRequest,
    db: DbSession,
    current_user: CurrentUser,
    provider: PaymentProviderDep,
) -> PurchaseResponse:
    return await membership_service.purchase_membership(
        db,
        payload,
        actor=current_user,
        provider=provider,
    )


@router.get("/{membership_id}", response_model=MembershipRead, summary="Абонемент по ID")
async def get_membership(
    membership_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> MembershipRead:
    membership = await membership_service.get_membership_for_actor(db, membership_id, current_user)
    return MembershipRead.model_validate(membership)


@router.post(
    "/{membership_id}/cancel",
    response_model=MembershipRead,
    summary="Отменить абонемент",
)
async def cancel_membership(
    membership_id: uuid.UUID,
    db: DbSession,
    _: AdminUser,
) -> MembershipRead:
    membership = await membership_service.get_membership_or_404(db, membership_id)
    updated = await membership_service.cancel_membership(db, membership)
    return MembershipRead.model_validate(updated)
