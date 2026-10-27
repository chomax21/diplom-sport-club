import uuid
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import AdminUser, CurrentUser, DbSession, PaymentProviderDep
from app.models.enums import PaymentStatus
from app.schemas.common import Page
from app.schemas.payment import PaymentRead
from app.services import payments as payment_service

router = APIRouter(prefix="/payments", tags=["Платежи"])


@router.get("", response_model=Page[PaymentRead], summary="Список платежей")
async def list_payments(
    db: DbSession,
    current_user: CurrentUser,
    status: PaymentStatus | None = None,
    client_id: uuid.UUID | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[PaymentRead]:
    items, total = await payment_service.list_payments(
        db,
        actor=current_user,
        status=status,
        client_id=client_id,
        limit=limit,
        offset=offset,
    )
    return Page(
        items=[PaymentRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{payment_id}", response_model=PaymentRead, summary="Платёж по ID")
async def get_payment(
    payment_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> PaymentRead:
    payment = await payment_service.get_payment_for_actor(db, payment_id, current_user)
    return PaymentRead.model_validate(payment)


@router.post(
    "/{payment_id}/refund",
    response_model=PaymentRead,
    summary="Вернуть платёж",
)
async def refund_payment(
    payment_id: uuid.UUID,
    db: DbSession,
    _: AdminUser,
    provider: PaymentProviderDep,
) -> PaymentRead:
    payment = await payment_service.get_payment_or_404(db, payment_id)
    refunded = await payment_service.refund_payment(db, payment, provider=provider)
    return PaymentRead.model_validate(refunded)
