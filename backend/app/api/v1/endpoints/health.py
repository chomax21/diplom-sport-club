from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.deps import DbSession
from app.core.config import settings

router = APIRouter(tags=["Служебные"])


@router.get("/health", summary="Проверка работоспособности")
async def health(db: DbSession) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="База данных недоступна") from exc
    return {
        "status": "ok",
        "database": "ok",
        "version": settings.app_version,
    }
