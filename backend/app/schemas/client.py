import uuid
from datetime import date, datetime

from pydantic import Field

from app.schemas.common import ORMModel


class ClientUpdate(ORMModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    birth_date: date | None = None
    notes: str | None = None
    emergency_contact: str | None = Field(default=None, max_length=255)


class ClientRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    email: str
    phone: str | None
    birth_date: date | None
    notes: str | None
    emergency_contact: str | None
    is_active: bool
    created_at: datetime
