from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine
from app.core.exceptions import AppError

tags_metadata = [
    {"name": "Авторизация", "description": "Регистрация, вход, JWT-токены."},
    {"name": "Пользователи", "description": "Учётные записи и роли (администратор)."},
    {"name": "Клиенты", "description": "Профили клиентов клуба."},
    {"name": "Тренеры", "description": "Профили тренеров."},
    {"name": "Виды абонементов", "description": "Справочник абонементов."},
    {"name": "Абонементы", "description": "Оформление и учёт абонементов."},
    {"name": "Залы", "description": "Помещения клуба."},
    {"name": "Расписание тренировок", "description": "Групповые тренировки и запись."},
    {"name": "Записи и посещаемость", "description": "Запись, отмена, посещение."},
    {"name": "Платежи", "description": "Mock-платежи и возвраты."},
    {"name": "Отчёты", "description": "Посещаемость и выручка."},
    {"name": "Служебные", "description": "Health-check и корневой маршрут."},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Информационная система спортивного клуба: клиенты, тренеры, "
        "абонементы, расписание, запись, посещаемость и платежи."
    ),
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )


app.include_router(health_router)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["Служебные"], summary="Корневой маршрут")
async def root() -> dict[str, str]:
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
