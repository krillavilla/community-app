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
    SeedCreate,
    SeedResponse,
    SeedSummary,
    VineResponse,
    SoilCreate,
    SoilResponse,
    FeedRequest,
    FeedResponse,
    WaterResponse,
    SunlightResponse,
    VoteResponse,
    SearchRequest,
    ClimateReadingResponse
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
    # Garden System
    "SeedCreate",
    "SeedResponse",
    "SeedSummary",
    "VineResponse",
    "SoilCreate",
    "SoilResponse",
    "FeedRequest",
    "FeedResponse",
    "WaterResponse",
    "SunlightResponse",
    "VoteResponse",
    "SearchRequest",
    "ClimateReadingResponse",
]
