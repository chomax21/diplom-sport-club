from datetime import UTC, date, datetime, time


def utcnow() -> datetime:
    return datetime.now(UTC)


def ensure_utc(value: datetime) -> datetime:
    """SQLite теряет tzinfo, PostgreSQL возвращает aware datetime."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def day_start(value: date) -> datetime:
    return datetime.combine(value, time.min, tzinfo=UTC)


def day_end(value: date) -> datetime:
    return datetime.combine(value, time.max, tzinfo=UTC)
