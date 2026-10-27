from datetime import date
from decimal import Decimal

from app.schemas.common import ORMModel


class DailyAttendance(ORMModel):
    day: date
    enrollments: int
    attended: int


class AttendanceReport(ORMModel):
    date_from: date
    date_to: date
    sessions_count: int
    enrollments_count: int
    attended_count: int
    no_show_count: int
    attendance_rate: float
    by_day: list[DailyAttendance]


class RevenueByMembershipType(ORMModel):
    membership_type_name: str
    payments_count: int
    amount: Decimal


class DailyRevenue(ORMModel):
    day: date
    payments_count: int
    amount: Decimal


class RevenueReport(ORMModel):
    date_from: date
    date_to: date
    payments_count: int
    total_amount: Decimal
    refunded_amount: Decimal
    by_membership_type: list[RevenueByMembershipType]
    by_day: list[DailyRevenue]
