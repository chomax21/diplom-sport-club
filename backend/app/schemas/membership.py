import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import Field

from app.models.enums import MembershipStatus, PaymentMethod
from app.schemas.common import ORMModel
from app.schemas.payment import PaymentRead


class MembershipTypeCreate(ORMModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    duration_days: int = Field(gt=0, le=3650)
    visits_limit: int | None = Field(default=None, gt=0, le=10000)
    is_active: bool = True


class MembershipTypeUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    duration_days: int | None = Field(default=None, gt=0, le=3650)
    visits_limit: int | None = Field(default=None, gt=0, le=10000)
    is_active: bool | None = None


class MembershipTypeRead(ORMModel):
    id: uuid.UUID
    name: str
    description: str | None
    price: Decimal
    duration_days: int
    visits_limit: int | None
    is_active: bool
    is_unlimited: bool


class MembershipRead(ORMModel):
    id: uuid.UUID
    client_id: uuid.UUID
    client_name: str
    membership_type_id: uuid.UUID
    membership_type_name: str
    starts_at: date
    ends_at: date
    visits_left: int | None
    status: MembershipStatus
    created_at: datetime


class PurchaseRequest(ORMModel):
    membership_type_id: uuid.UUID
    client_id: uuid.UUID | None = None
    payment_method: PaymentMethod = PaymentMethod.CARD


class PurchaseResponse(ORMModel):
    membership: MembershipRead
    payment: PaymentRead
