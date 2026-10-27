from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from app.models.enums import PaymentStatus


@dataclass(slots=True)
class PaymentResult:
    external_id: str
    status: PaymentStatus
    raw: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class PaymentProvider(ABC):
    """Контракт платёжного провайдера.

    Чтобы подключить реальный шлюз (ЮKassa, CloudPayments и т.п.),
    достаточно реализовать этот интерфейс и зарегистрировать класс
    в app/integrations/payments/factory.py.
    """

    name: str

    @abstractmethod
    async def create_payment(
        self,
        *,
        amount: Decimal,
        currency: str,
        description: str,
        metadata: dict[str, Any],
    ) -> PaymentResult:
        """Инициирует платёж и возвращает результат."""

    @abstractmethod
    async def refund(
        self,
        *,
        external_id: str,
        amount: Decimal,
        currency: str,
    ) -> PaymentResult:
        """Возвращает средства по ранее созданному платежу."""
