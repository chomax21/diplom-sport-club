import uuid

from pydantic import Field

from app.schemas.common import ORMModel


class RoomCreate(ORMModel):
    name: str = Field(min_length=1, max_length=120)
    capacity: int = Field(gt=0, le=10000)
    description: str | None = None
    is_active: bool = True


class RoomUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    capacity: int | None = Field(default=None, gt=0, le=10000)
    description: str | None = None
    is_active: bool | None = None


class RoomRead(ORMModel):
    id: uuid.UUID
    name: str
    capacity: int
    description: str | None
    is_active: bool
