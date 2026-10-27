from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, PaymentError
from app.core.pagination import paginate
from app.core.time import utcnow
from app.integrations.payments.base import PaymentProvider
from app.models import (
    ClientProfile,
    Enrollment,
    EnrollmentStatus,
    MembershipStatus,
    Payment,
    PaymentStatus,
    User,
    UserRole,
)
from app.services.clients import get_client_by_user_id_or_404


def _payment_options():
    return (
        joinedload(Payment.client).joinedload(ClientProfile.user),
        joinedload(Payment.membership),
    )


async def get_payment_or_404(db: AsyncSession, payment_id: uuid.UUID) -> Payment:
    payment = await db.scalar(
        select(Payment).where(Payment.id == payment_id).options(*_payment_options())
    )
    if payment is None:
        raise NotFoundError("Платёж не найден")
    return payment


async def list_payments(
    db: AsyncSession,
    *,
    actor: User,
    status: PaymentStatus | None,
    client_id: uuid.UUID | None,
    limit: int,
    offset: int,
) -> tuple[list[Payment], int]:
    stmt = select(Payment).options(*_payment_options())

    if actor.role == UserRole.ADMIN:
        if client_id is not None:
            stmt = stmt.where(Payment.client_id == client_id)
    elif actor.role == UserRole.CLIENT:
        client = await get_client_by_user_id_or_404(db, actor.id)
        if client_id is not None and client_id != client.id:
            raise ForbiddenError("Можно просматривать только свои платежи")
        stmt = stmt.where(Payment.client_id == client.id)
    else:
        raise ForbiddenError("Тренер не имеет доступа к платежам")

    if status is not None:
        stmt = stmt.where(Payment.status == status)

    stmt = stmt.order_by(Payment.created_at.desc())
    return await paginate(db, stmt, limit=limit, offset=offset)


async def get_payment_for_actor(
    db: AsyncSession,
    payment_id: uuid.UUID,
    actor: User,
) -> Payment:
    payment = await get_payment_or_404(db, payment_id)
    if actor.role == UserRole.ADMIN:
        return payment
    if actor.role == UserRole.CLIENT:
        client = await get_client_by_user_id_or_404(db, actor.id)
        if payment.client_id == client.id:
            return payment
    raise ForbiddenError("Нет доступа к этому платежу")


async def refund_payment(
    db: AsyncSession,
    payment: Payment,
    *,
    provider: PaymentProvider,
) -> Payment:
    if payment.status != PaymentStatus.SUCCEEDED:
        raise ConflictError("Вернуть можно только успешный платёж")

    refund_raw: dict = {"manual": payment.provider == "manual"}
    if payment.provider == "manual":
        refund_raw["note"] = "Возврат наличными оформлен администратором"
    else:
        if not payment.external_id:
            raise PaymentError("У платежа отсутствует внешний идентификатор")
        try:
            result = await provider.refund(
                external_id=payment.external_id,
                amount=payment.amount,
                currency=payment.currency,
            )
        except Exception as exc:
            raise PaymentError("Платёжный провайдер не подтвердил возврат") from exc
        if result.status != PaymentStatus.REFUNDED:
            raise PaymentError(result.error or "Возврат отклонён провайдером")
        refund_raw["provider_response"] = result.raw

    if payment.membership_id is not None:
        attended_count = await db.scalar(
            select(func.count(Enrollment.id)).where(
                Enrollment.membership_id == payment.membership_id,
                Enrollment.status == EnrollmentStatus.ATTENDED,
            )
        )
        if attended_count:
            raise ConflictError("Нельзя вернуть платёж: по абонементу уже есть посещения")

    payment.status = PaymentStatus.REFUNDED
    payment.refunded_at = utcnow()
    payment.extra = {**(payment.extra or {}), "refund": refund_raw}

    if payment.membership is not None:
        payment.membership.status = MembershipStatus.CANCELLED
        if payment.membership.visits_left is not None:
            payment.membership.visits_left = 0

    await db.commit()
    return await get_payment_or_404(db, payment.id)
