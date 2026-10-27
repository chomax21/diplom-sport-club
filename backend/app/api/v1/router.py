from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    clients,
    enrollments,
    membership_types,
    memberships,
    payments,
    reports,
    rooms,
    sessions,
    trainers,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(clients.router)
api_router.include_router(trainers.router)
api_router.include_router(membership_types.router)
api_router.include_router(memberships.router)
api_router.include_router(rooms.router)
api_router.include_router(sessions.router)
api_router.include_router(enrollments.router)
api_router.include_router(payments.router)
api_router.include_router(reports.router)
