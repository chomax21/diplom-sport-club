from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import hash_password
from app.main import app
from app.models import (
    Base,
    ClientProfile,
    TrainerProfile,
    User,
    UserRole,
)

TEST_PASSWORD = "Password123"
TEST_PASSWORD_HASH = hash_password(TEST_PASSWORD)

test_engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionFactory = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture
async def db() -> AsyncIterator[AsyncSession]:
    async with TestSessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with TestSessionFactory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client
    app.dependency_overrides.clear()


async def create_user(
    db: AsyncSession,
    *,
    email: str,
    full_name: str,
    role: UserRole,
) -> User:
    user = User(
        email=email,
        hashed_password=TEST_PASSWORD_HASH,
        full_name=full_name,
        role=role,
    )
    db.add(user)
    await db.flush()
    if role == UserRole.CLIENT:
        db.add(ClientProfile(user_id=user.id))
    elif role == UserRole.TRAINER:
        db.add(TrainerProfile(user_id=user.id, specialization="ОФП"))
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession) -> User:
    return await create_user(
        db,
        email="admin@example.com",
        full_name="Администратор",
        role=UserRole.ADMIN,
    )


@pytest_asyncio.fixture
async def trainer_user(db: AsyncSession) -> User:
    return await create_user(
        db,
        email="trainer@example.com",
        full_name="Тренер",
        role=UserRole.TRAINER,
    )


@pytest_asyncio.fixture
async def client_user(db: AsyncSession) -> User:
    return await create_user(
        db,
        email="client@example.com",
        full_name="Клиент",
        role=UserRole.CLIENT,
    )


@pytest_asyncio.fixture
async def trainer_profile(db: AsyncSession, trainer_user: User) -> TrainerProfile:
    profile = await db.scalar(
        select(TrainerProfile).where(TrainerProfile.user_id == trainer_user.id)
    )
    assert profile is not None
    return profile


@pytest.fixture
def auth_headers():
    def make(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    return make


async def _login(client: AsyncClient, email: str) -> str:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient, admin_user: User) -> str:
    return await _login(client, admin_user.email)


@pytest_asyncio.fixture
async def trainer_token(client: AsyncClient, trainer_user: User) -> str:
    return await _login(client, trainer_user.email)


@pytest_asyncio.fixture
async def client_token(client: AsyncClient, client_user: User) -> str:
    return await _login(client, client_user.email)


@pytest_asyncio.fixture
async def membership_type(
    client: AsyncClient,
    admin_token: str,
    auth_headers,
) -> dict:
    response = await client.post(
        "/api/v1/membership-types",
        json={
            "name": "Месяц (12 посещений)",
            "description": "Тестовый абонемент",
            "price": "4500.00",
            "duration_days": 30,
            "visits_limit": 12,
        },
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest_asyncio.fixture
async def room(
    client: AsyncClient,
    admin_token: str,
    auth_headers,
) -> dict:
    response = await client.post(
        "/api/v1/rooms",
        json={"name": "Зал 1", "capacity": 20},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest_asyncio.fixture
async def training_session(
    client: AsyncClient,
    admin_token: str,
    auth_headers,
    room: dict,
    trainer_profile: TrainerProfile,
) -> dict:
    starts_at = (datetime.now(UTC) + timedelta(days=1)).replace(
        hour=18, minute=0, second=0, microsecond=0
    )
    response = await client.post(
        "/api/v1/sessions",
        json={
            "title": "Функциональный тренинг",
            "trainer_id": str(trainer_profile.id),
            "room_id": room["id"],
            "starts_at": starts_at.isoformat(),
            "ends_at": (starts_at + timedelta(minutes=90)).isoformat(),
            "capacity": 5,
        },
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest_asyncio.fixture
async def purchase(
    client: AsyncClient,
    client_token: str,
    auth_headers,
    membership_type: dict,
) -> dict:
    response = await client.post(
        "/api/v1/memberships/purchase",
        json={"membership_type_id": membership_type["id"]},
        headers=auth_headers(client_token),
    )
    assert response.status_code == 201, response.text
    return response.json()
