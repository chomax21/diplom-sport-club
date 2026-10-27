from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, enum_type
from app.models.enums import MembershipStatus

if TYPE_CHECKING:
    from app.models.user import ClientProfile


class MembershipType(TimestampMixin, Base):
    __tablename__ = "membership_types"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_membership_types_price_non_negative"),
        CheckConstraint("duration_days > 0", name="ck_membership_types_duration_positive"),
        CheckConstraint(
            "visits_limit IS NULL OR visits_limit > 0",
            name="ck_membership_types_visits_positive",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    visits_limit: Mapped[int | None] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    @property
    def is_unlimited(self) -> bool:
        return self.visits_limit is None


class Membership(TimestampMixin, Base):
    __tablename__ = "memberships"
    __table_args__ = (
        CheckConstraint(
            "visits_left IS NULL OR visits_left >= 0",
            name="ck_memberships_visits_left_non_negative",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("client_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    membership_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("membership_types.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    starts_at: Mapped[date] = mapped_column(Date, nullable=False)
    ends_at: Mapped[date] = mapped_column(Date, nullable=False)
    visits_left: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[MembershipStatus] = mapped_column(
        enum_type(MembershipStatus, "membership_status"),
        default=MembershipStatus.PENDING,
        nullable=False,
        index=True,
    )

    client: Mapped[ClientProfile] = relationship("ClientProfile", lazy="raise")
    membership_type: Mapped[MembershipType] = relationship("MembershipType", lazy="raise")

    @property
    def client_name(self) -> str:
        return self.client.user.full_name

    @property
    def membership_type_name(self) -> str:
        return self.membership_type.name
