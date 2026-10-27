from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    PaymentError,
)
from app.core.pagination import paginate
from app.core.time import utcnow
from app.integrations.payments.base import PaymentProvider
from app.models import (
    ClientProfile,
    Membership,
    MembershipStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    User,
    UserRole,
)
from app.schemas.membership import MembershipRead, PurchaseRequest, PurchaseResponse
from app.schemas.payment import PaymentRead
from app.services.clients import get_client_by_user_id_or_404, get_client_or_404
from app.services.membership_types import get_membership_type_or_404
from app.services.payments import get_payment_or_404


def _membership_options():
    return (
        joinedload(Membership.client).joinedload(ClientProfile.user),
        joinedload(Membership.membership_type),
    )


async def get_membership_or_404(db: AsyncSession, membership_id: uuid.UUID) -> Membership:
    membership = await db.scalar(
        select(Membership).where(Membership.id == membership_id).options(*_membership_options())
    )
    if membership is None:
        raise NotFoundError("Абонемент не найден")
    return membership


async def list_memberships(
    db: AsyncSession,
    *,
    actor: User,
    status: MembershipStatus | None,
    client_id: uuid.UUID | None,
    limit: int,
    offset: int,
) -> tuple[list[Membership], int]:
    stmt = select(Membership).options(*_membership_options())

    if actor.role == UserRole.ADMIN:
        if client_id is not None:
            stmt = stmt.where(Membership.client_id == client_id)
    elif actor.role == UserRole.CLIENT:
        client = await get_client_by_user_id_or_404(db, actor.id)
        if client_id is not None and client_id != client.id:
            raise ForbiddenError("Можно просматривать только свои абонементы")
        stmt = stmt.where(Membership.client_id == client.id)
    else:
        raise ForbiddenError("Тренер не имеет доступа к абонементам клиентов")

    if status is not None:
        stmt = stmt.where(Membership.status == status)

    stmt = stmt.order_by(Membership.created_at.desc())
    return await paginate(db, stmt, limit=limit, offset=offset)


async def get_membership_for_actor(
    db: AsyncSession,
    membership_id: uuid.UUID,
    actor: User,
) -> Membership:
    membership = await get_membership_or_404(db, membership_id)
    if actor.role == UserRole.ADMIN:
        return membership
    if actor.role == UserRole.CLIENT:
        client = await get_client_by_user_id_or_404(db, actor.id)
        if membership.client_id == client.id:
            return membership
    raise ForbiddenError("Нет доступа к этому абонементу")


async def purchase_membership(
    db: AsyncSession,
    payload: PurchaseRequest,
    *,
    actor: User,
    provider: PaymentProvider,
) -> PurchaseResponse:
    if actor.role == UserRole.TRAINER:
        raise ForbiddenError("Тренер не может оформлять абонементы")

    if actor.role == UserRole.ADMIN:
        if payload.client_id is None:
            raise ConflictError("Для оформления абонемента администратором укажите client_id")
        client = await get_client_or_404(db, payload.client_id)
    else:
        client = await get_client_by_user_id_or_404(db, actor.id)
        if payload.client_id is not None and payload.client_id != client.id:
            raise ForbiddenError("Можно оформить абонемент только на себя")

    membership_type = await get_membership_type_or_404(db, payload.membership_type_id)
    if not membership_type.is_active:
        raise ConflictError("Этот вид абонемента недоступен для продажи")

    if payload.payment_method == PaymentMethod.CASH and actor.role != UserRole.ADMIN:
        raise ForbiddenError("Оплата наличными оформляется только администратором")

    today = utcnow().date()
    membership = Membership(
        client_id=client.id,
        membership_type_id=membership_type.id,
        starts_at=today,
        ends_at=today + timedelta(days=membership_type.duration_days),
        visits_left=membership_type.visits_limit,
        status=MembershipStatus.PENDING,
    )
    db.add(membership)
    await db.flush()

    is_manual = payload.payment_method == PaymentMethod.CASH
    payment = Payment(
        client_id=client.id,
        membership_id=membership.id,
        amount=membership_type.price,
        currency=settings.default_currency,
        status=PaymentStatus.PENDING,
        provider="manual" if is_manual else provider.name,
        payment_method=payload.payment_method,
        description=f"Абонемент «{membership_type.name}»",
        extra={},
    )
    db.add(payment)
    await db.flush()

    if is_manual:
        payment.status = PaymentStatus.SUCCEEDED
        payment.paid_at = utcnow()
        payment.extra = {
            "manual": True,
            "registered_by": str(actor.id),
            "note": "Оплата наличными в клубе",
        }
        membership.status = MembershipStatus.ACTIVE
    else:
        try:
            result = await provider.create_payment(
                amount=membership_type.price,
                currency=settings.default_currency,
                description=payment.description or "Оплата абонемента",
                metadata={
                    "membership_id": str(membership.id),
                    "payment_id": str(payment.id),
                    "client_id": str(client.id),
                },
            )
        except Exception as exc:
            payment.status = PaymentStatus.FAILED
            membership.status = MembershipStatus.CANCELLED
            await db.commit()
            raise PaymentError("Платёжный провайдер недоступен, попробуйте позже") from exc

        payment.external_id = result.external_id
        payment.extra = result.raw
        if result.status == PaymentStatus.SUCCEEDED:
            payment.status = PaymentStatus.SUCCEEDED
            payment.paid_at = utcnow()
            membership.status = MembershipStatus.ACTIVE
        else:
            payment.status = PaymentStatus.FAILED
            membership.status = MembershipStatus.CANCELLED
            await db.commit()
            raise PaymentError(result.error or "Платёж отклонён провайдером")

    await db.commit()

    saved_membership = await get_membership_or_404(db, membership.id)
    saved_payment = await get_payment_or_404(db, payment.id)
    return PurchaseResponse(
        membership=MembershipRead.model_validate(saved_membership),
        payment=PaymentRead.model_validate(saved_payment),
    )


async def cancel_membership(db: AsyncSession, membership: Membership) -> Membership:
    if membership.status == MembershipStatus.CANCELLED:
        raise ConflictError("Абонемент уже отменён")
    membership.status = MembershipStatus.CANCELLED
    if membership.visits_left is not None:
        membership.visits_left = 0
    await db.commit()
    return await get_membership_or_404(db, membership.id)


__all__ = [
    "cancel_membership",
    "get_membership_for_actor",
    "get_membership_or_404",
    "list_memberships",
    "purchase_membership",
]
