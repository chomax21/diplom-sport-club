from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def enum_type(enum_cls: type[Enum], name: str) -> SAEnum:
    """Хранит enum как VARCHAR, а не как нативный тип PostgreSQL.

    Это упрощает миграции и делает схему переносимой (в тестах — SQLite).
    """
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        length=20,
        values_callable=lambda members: [member.value for member in members],
    )
