import uuid
from decimal import Decimal
from typing import Any

from app.integrations.payments.base import PaymentProvider, PaymentResult
from app.models.enums import PaymentStatus


class MockPaymentProvider(PaymentProvider):
    """Имитация платёжного шлюза для дипломного прототипа.

    Платёж всегда успешен, но проходит полный жизненный цикл:
    pending -> succeeded, возвращает внешний идентификатор и сохраняет
    «сырой» ответ провайдера в Payment.extra.
    """

    name = "mock"

    async def create_payment(
        self,
        *,
        amount: Decimal,
        currency: str,
        description: str,
        metadata: dict[str, Any],
    ) -> PaymentResult:
        external_id = f"mock-{uuid.uuid4().hex}"
        return PaymentResult(
            external_id=external_id,
            status=PaymentStatus.SUCCEEDED,
            raw={
                "provider": self.name,
                "amount": str(amount),
                "currency": currency,
                "description": description,
                "metadata": metadata,
                "test_mode": True,
            },
        )

    async def refund(
        self,
        *,
        external_id: str,
        amount: Decimal,
        currency: str,
    ) -> PaymentResult:
        return PaymentResult(
            external_id=external_id,
            status=PaymentStatus.REFUNDED,
            raw={
                "provider": self.name,
                "refund_amount": str(amount),
                "currency": currency,
                "test_mode": True,
            },
        )
