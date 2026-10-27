from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate(
    db: AsyncSession,
    stmt: Select[Any],
    *,
    limit: int,
    offset: int,
) -> tuple[list[Any], int]:
    """Возвращает страницу результатов и общее количество строк."""
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = await db.scalar(count_stmt) or 0
    result = await db.scalars(stmt.limit(limit).offset(offset))
    return list(result.all()), int(total)
