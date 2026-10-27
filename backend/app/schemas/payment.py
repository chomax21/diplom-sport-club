import uuid
from datetime import datetime
from decimal import Decimal

from app.models.enums import PaymentMethod, PaymentStatus
from app.schemas.common import ORMModel


class PaymentRead(ORMModel):
    id: uuid.UUID
    client_id: uuid.UUID
    client_name: str
    membership_id: uuid.UUID | None
    amount: Decimal
    currency: str
    status: PaymentStatus
    provider: str
    external_id: str | None
    payment_method: PaymentMethod
    description: str | None
    paid_at: datetime | None
    refunded_at: datetime | None
    created_at: datetime
