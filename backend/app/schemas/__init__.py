"""
Pydantic schemas package exports.

TODO: Create individual schema files for each feature as needed.
For now, importing from user and garden schemas.
"""
from app.schemas.base import BaseSchema, IDMixin, TimestampMixin, PaginationParams, PaginatedResponse
from app.schemas.user import (
    UserBase,
    UserUpdate,
    UserResponse,
    GuideApplicationCreate,
    GuideApplicationResponse,
    GuideApplicationReview,
    TrustVerificationApplicationCreate,
    TrustVerificationApplicationResponse,
    TrustVerificationReview
)
from app.schemas.garden import (
    HabitCreate,
    HabitUpdate,
    HabitResponse,
    HabitLogCreate,
    HabitLogResponse,
    GardenResponse
)

__all__ = [
    # Base
    "BaseSchema",
    "IDMixin",
    "TimestampMixin",
    "PaginationParams",
    "PaginatedResponse",
    # User
    "UserBase",
    "UserUpdate",
    "UserResponse",
    "GuideApplicationCreate",
    "GuideApplicationResponse",
    "GuideApplicationReview",
    "TrustVerificationApplicationCreate",
    "TrustVerificationApplicationResponse",
    "TrustVerificationReview",
    # Garden
    "HabitCreate",
    "HabitUpdate",
    "HabitResponse",
    "HabitLogCreate",
    "HabitLogResponse",
    "GardenResponse",
]
