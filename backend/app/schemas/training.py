import uuid
from datetime import datetime

from pydantic import Field, field_validator

from app.models.enums import EnrollmentStatus
from app.schemas.common import ORMModel


def _require_timezone(value: datetime | None) -> datetime | None:
    if value is not None and value.tzinfo is None:
        raise ValueError("Дата и время должны содержать часовой пояс (например, Z)")
    return value


class TrainingSessionCreate(ORMModel):
    title: str = Field(min_length=2, max_length=255)
    trainer_id: uuid.UUID | None = None
    room_id: uuid.UUID
    starts_at: datetime
    ends_at: datetime
    capacity: int = Field(gt=0, le=10000)
    description: str | None = None

    @field_validator("starts_at", "ends_at")
    @classmethod
    def validate_timezone(cls, value: datetime) -> datetime:
        result = _require_timezone(value)
        assert result is not None
        return result


class TrainingSessionUpdate(ORMModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    trainer_id: uuid.UUID | None = None
    room_id: uuid.UUID | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    capacity: int | None = Field(default=None, gt=0, le=10000)
    description: str | None = None

    @field_validator("starts_at", "ends_at")
    @classmethod
    def validate_timezone(cls, value: datetime | None) -> datetime | None:
        return _require_timezone(value)


class TrainingSessionRead(ORMModel):
    id: uuid.UUID
    title: str
    trainer_id: uuid.UUID
    trainer_name: str
    room_id: uuid.UUID
    room_name: str
    starts_at: datetime
    ends_at: datetime
    capacity: int
    enrolled_count: int
    available_slots: int
    description: str | None
    is_cancelled: bool
    created_at: datetime


class EnrollmentCreate(ORMModel):
    client_id: uuid.UUID | None = None


class AttendanceMark(ORMModel):
    note: str | None = None


class EnrollmentRead(ORMModel):
    id: uuid.UUID
    session_id: uuid.UUID
    client_id: uuid.UUID
    client_name: str
    client_phone: str | None
    client_email: str
    status: EnrollmentStatus
    is_attended: bool
    created_at: datetime
    cancelled_at: datetime | None
