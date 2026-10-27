from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DbSession
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
)
from app.schemas.user import UserRead
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["Авторизация"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
    summary="Регистрация клиента",
)
async def register(payload: RegisterRequest, db: DbSession) -> UserRead:
    user = await auth_service.register_client(db, payload)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenPair, summary="Вход по email и паролю")
async def login(payload: LoginRequest, db: DbSession) -> TokenPair:
    user = await auth_service.authenticate(db, payload.email, payload.password)
    return auth_service.issue_tokens(user)


@router.post(
    "/token",
    response_model=TokenPair,
    summary="Вход для Swagger (OAuth2 password flow)",
)
async def login_form(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> TokenPair:
    user = await auth_service.authenticate(db, form.username, form.password)
    return auth_service.issue_tokens(user)


@router.post("/refresh", response_model=TokenPair, summary="Обновление пары токенов")
async def refresh(payload: RefreshRequest, db: DbSession) -> TokenPair:
    return await auth_service.refresh_tokens(db, payload.refresh_token)


@router.get("/me", response_model=UserRead, summary="Текущий пользователь")
async def me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
