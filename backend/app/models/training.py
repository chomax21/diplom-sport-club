from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, enum_type
from app.models.enums import EnrollmentStatus

if TYPE_CHECKING:
    from app.models.membership import Membership
    from app.models.user import ClientProfile, TrainerProfile, User


class Room(TimestampMixin, Base):
    __tablename__ = "rooms"
    __table_args__ = (CheckConstraint("capacity > 0", name="ck_rooms_capacity_positive"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class TrainingSession(TimestampMixin, Base):
    __tablename__ = "training_sessions"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ck_training_sessions_time_order"),
        CheckConstraint("capacity > 0", name="ck_training_sessions_capacity_positive"),
        Index("ix_training_sessions_starts_at", "starts_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    trainer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("trainer_profiles.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    room_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("rooms.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_cancelled: Mapped[bool] = mapped_column(default=False, nullable=False)

    trainer: Mapped[TrainerProfile] = relationship("TrainerProfile", lazy="raise")
    room: Mapped[Room] = relationship("Room", lazy="raise")
    enrollments: Mapped[list[Enrollment]] = relationship(
        "Enrollment",
        back_populates="session",
        lazy="raise",
        cascade="all, delete-orphan",
    )

    @property
    def trainer_name(self) -> str:
        return self.trainer.user.full_name

    @property
    def room_name(self) -> str:
        return self.room.name

    @property
    def enrolled_count(self) -> int:
        return sum(1 for item in self.enrollments if item.status == EnrollmentStatus.ACTIVE)

    @property
    def available_slots(self) -> int:
        return max(self.capacity - self.enrolled_count, 0)


class Enrollment(TimestampMixin, Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("session_id", "client_id", name="uq_enrollments_session_client"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("training_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("client_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    membership_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("memberships.id", ondelete="SET NULL"),
        index=True,
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        enum_type(EnrollmentStatus, "enrollment_status"),
        default=EnrollmentStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    session: Mapped[TrainingSession] = relationship(
        "TrainingSession",
        back_populates="enrollments",
        lazy="raise",
    )
    client: Mapped[ClientProfile] = relationship("ClientProfile", lazy="raise")
    membership: Mapped[Membership | None] = relationship("Membership", lazy="raise")
    attendance: Mapped[Attendance | None] = relationship(
        "Attendance",
        lazy="raise",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def client_name(self) -> str:
        return self.client.user.full_name

    @property
    def client_phone(self) -> str | None:
        return self.client.user.phone

    @property
    def client_email(self) -> str:
        return self.client.user.email

    @property
    def is_attended(self) -> bool:
        return self.attendance is not None


class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enrollment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("enrollments.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    marked_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    marked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    note: Mapped[str | None] = mapped_column(Text)

    marked_by: Mapped[User] = relationship("User", lazy="raise")
