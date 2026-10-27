"""Идемпотентное наполнение базы демонстрационными данными.

Запуск внутри контейнера:
    docker compose exec backend python -m app.seed
"""

import asyncio
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.database import async_session_factory, engine
from app.core.security import hash_password
from app.models import (
    Attendance,
    ClientProfile,
    Enrollment,
    EnrollmentStatus,
    Membership,
    MembershipStatus,
    MembershipType,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Room,
    TrainerProfile,
    TrainingSession,
    User,
    UserRole,
)

ADMIN_EMAIL = "admin@sportsclub.ru"
ADMIN_PASSWORD = "Admin12345"
TRAINER_EMAIL = "trainer@sportsclub.ru"
TRAINER_PASSWORD = "Trainer12345"
CLIENT_EMAIL = "client@sportsclub.ru"
CLIENT_PASSWORD = "Client12345"


async def get_or_create_user(
    db,
    *,
    email: str,
    password: str,
    full_name: str,
    role: UserRole,
    phone: str | None = None,
) -> User:
    user = await db.scalar(select(User).where(User.email == email))
    if user is not None:
        return user

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        phone=phone,
        role=role,
    )
    db.add(user)
    await db.flush()
    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_trainer_profile(db, user: User) -> TrainerProfile:
    profile = await db.scalar(select(TrainerProfile).where(TrainerProfile.user_id == user.id))
    if profile is None:
        profile = TrainerProfile(
            user_id=user.id,
            specialization="Функциональный тренинг, ОФП",
            bio="Тренер клуба с опытом работы более 7 лет.",
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


async def get_or_create_client_profile(db, user: User) -> ClientProfile:
    profile = await db.scalar(select(ClientProfile).where(ClientProfile.user_id == user.id))
    if profile is None:
        profile = ClientProfile(
            user_id=user.id,
            birth_date=date(1995, 5, 20),
            emergency_contact="+7 900 000-00-00",
        )
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


async def get_or_create_membership_type(
    db,
    *,
    name: str,
    price: Decimal,
    duration_days: int,
    visits_limit: int | None,
    description: str,
) -> MembershipType:
    membership_type = await db.scalar(select(MembershipType).where(MembershipType.name == name))
    if membership_type is None:
        membership_type = MembershipType(
            name=name,
            description=description,
            price=price,
            duration_days=duration_days,
            visits_limit=visits_limit,
        )
        db.add(membership_type)
        await db.commit()
        await db.refresh(membership_type)
    return membership_type


async def get_or_create_room(db, name: str, capacity: int, description: str) -> Room:
    room = await db.scalar(select(Room).where(Room.name == name))
    if room is None:
        room = Room(name=name, capacity=capacity, description=description)
        db.add(room)
        await db.commit()
        await db.refresh(room)
    return room


async def ensure_membership(
    db,
    *,
    client: ClientProfile,
    membership_type: MembershipType,
) -> Membership:
    membership = await db.scalar(select(Membership).where(Membership.client_id == client.id))
    if membership is not None:
        return membership

    today = date.today()
    membership = Membership(
        client_id=client.id,
        membership_type_id=membership_type.id,
        starts_at=today,
        ends_at=today + timedelta(days=membership_type.duration_days),
        visits_left=membership_type.visits_limit,
        status=MembershipStatus.ACTIVE,
    )
    db.add(membership)
    await db.flush()

    payment = Payment(
        client_id=client.id,
        membership_id=membership.id,
        amount=membership_type.price,
        currency="RUB",
        status=PaymentStatus.SUCCEEDED,
        provider="mock",
        external_id=f"mock-seed-{membership.id.hex[:16]}",
        payment_method=PaymentMethod.CARD,
        description=f"Абонемент «{membership_type.name}» (демо)",
        extra={"seed": True},
        paid_at=datetime.now(UTC),
    )
    db.add(payment)
    await db.commit()
    await db.refresh(membership)
    return membership


async def get_or_create_session(
    db,
    *,
    title: str,
    trainer: TrainerProfile,
    room: Room,
    starts_at: datetime,
    ends_at: datetime,
    capacity: int,
) -> TrainingSession:
    session = await db.scalar(
        select(TrainingSession).where(
            TrainingSession.title == title,
            TrainingSession.starts_at == starts_at,
        )
    )
    if session is None:
        session = TrainingSession(
            title=title,
            trainer_id=trainer.id,
            room_id=room.id,
            starts_at=starts_at,
            ends_at=ends_at,
            capacity=capacity,
            description="Демонстрационная групповая тренировка.",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
    return session


async def ensure_enrollment(
    db,
    *,
    session: TrainingSession,
    client: ClientProfile,
    membership: Membership,
) -> Enrollment:
    enrollment = await db.scalar(
        select(Enrollment).where(
            Enrollment.session_id == session.id,
            Enrollment.client_id == client.id,
        )
    )
    if enrollment is not None:
        return enrollment

    enrollment = Enrollment(
        session_id=session.id,
        client_id=client.id,
        membership_id=membership.id,
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


async def ensure_attended_enrollment(
    db,
    *,
    session: TrainingSession,
    client: ClientProfile,
    membership: Membership,
    marked_by_id,
) -> Enrollment:
    enrollment = await db.scalar(
        select(Enrollment).where(
            Enrollment.session_id == session.id,
            Enrollment.client_id == client.id,
        )
    )
    if enrollment is not None:
        return enrollment

    enrollment = Enrollment(
        session_id=session.id,
        client_id=client.id,
        membership_id=membership.id,
        status=EnrollmentStatus.ATTENDED,
    )
    db.add(enrollment)
    await db.flush()
    db.add(
        Attendance(
            enrollment_id=enrollment.id,
            marked_by_id=marked_by_id,
            marked_at=session.ends_at,
            note="Демонстрационное посещение",
        )
    )
    if membership.visits_left is not None and membership.visits_left > 0:
        membership.visits_left -= 1
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


async def seed() -> None:
    async with async_session_factory() as db:
        admin = await get_or_create_user(
            db,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            full_name="Администратор клуба",
            role=UserRole.ADMIN,
        )
        trainer_user = await get_or_create_user(
            db,
            email=TRAINER_EMAIL,
            password=TRAINER_PASSWORD,
            full_name="Иван Тренеров",
            role=UserRole.TRAINER,
            phone="+7 900 111-22-33",
        )
        client_user = await get_or_create_user(
            db,
            email=CLIENT_EMAIL,
            password=CLIENT_PASSWORD,
            full_name="Анна Клиентова",
            role=UserRole.CLIENT,
            phone="+7 900 444-55-66",
        )

        trainer = await get_or_create_trainer_profile(db, trainer_user)
        client = await get_or_create_client_profile(db, client_user)

        month_type = await get_or_create_membership_type(
            db,
            name="Месяц (12 посещений)",
            price=Decimal("4500.00"),
            duration_days=30,
            visits_limit=12,
            description="12 групповых тренировок в течение 30 дней.",
        )
        await get_or_create_membership_type(
            db,
            name="Разовое посещение",
            price=Decimal("800.00"),
            duration_days=1,
            visits_limit=1,
            description="Одна групповая тренировка.",
        )
        await get_or_create_membership_type(
            db,
            name="Безлимит на месяц",
            price=Decimal("6900.00"),
            duration_days=30,
            visits_limit=None,
            description="Неограниченное число тренировок в течение 30 дней.",
        )

        main_room = await get_or_create_room(
            db, "Зал 1", 20, "Основной зал для групповых тренировок."
        )
        await get_or_create_room(db, "Зал единоборств", 15, "Зал с покрытием для единоборств.")

        membership = await ensure_membership(db, client=client, membership_type=month_type)

        now = datetime.now(UTC)
        past_session = await get_or_create_session(
            db,
            title="Растяжка и мобильность",
            trainer=trainer,
            room=main_room,
            starts_at=(now - timedelta(days=3)).replace(hour=18, minute=0, second=0, microsecond=0),
            ends_at=(now - timedelta(days=3)).replace(hour=19, minute=0, second=0, microsecond=0),
            capacity=12,
        )
        await ensure_attended_enrollment(
            db,
            session=past_session,
            client=client,
            membership=membership,
            marked_by_id=admin.id,
        )

        tomorrow = (now + timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)
        day_after = tomorrow + timedelta(days=1)
        session = await get_or_create_session(
            db,
            title="Функциональный тренинг",
            trainer=trainer,
            room=main_room,
            starts_at=tomorrow,
            ends_at=tomorrow + timedelta(minutes=90),
            capacity=12,
        )
        await get_or_create_session(
            db,
            title="Силовая тренировка",
            trainer=trainer,
            room=main_room,
            starts_at=day_after.replace(hour=19),
            ends_at=day_after.replace(hour=20, minute=30),
            capacity=15,
        )
        await ensure_enrollment(db, session=session, client=client, membership=membership)

    print("Демо-данные готовы.")
    print(f"Администратор: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    print(f"Тренер:        {TRAINER_EMAIL} / {TRAINER_PASSWORD}")
    print(f"Клиент:        {CLIENT_EMAIL} / {CLIENT_PASSWORD}")


async def main() -> None:
    try:
        await seed()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
