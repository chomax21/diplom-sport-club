import uuid
from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMModel


class TrainerUpdate(ORMModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    specialization: str | None = Field(default=None, max_length=255)
    bio: str | None = None


class TrainerRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    email: str
    phone: str | None
    specialization: str | None
    bio: str | None
    is_active: bool
    created_at: datetime
