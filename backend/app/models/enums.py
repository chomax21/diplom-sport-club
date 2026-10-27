from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    TRAINER = "trainer"
    CLIENT = "client"


class MembershipStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    ATTENDED = "attended"
    NO_SHOW = "no_show"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CARD = "card"
    CASH = "cash"
    ONLINE = "online"
