"""
User and authentication Pydantic schemas.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole, TrustLevel, ApplicationStatus
from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


# User schemas
class UserBase(BaseSchema):
    """Base user fields."""
    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    spiritual_opt_in: bool = False


class UserUpdate(BaseSchema):
    """Schema for updating user profile."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    spiritual_opt_in: Optional[bool] = None


class UserResponse(UserBase, IDMixin, TimestampMixin):
    """Public user response."""
    role: UserRole
    trust_level: TrustLevel
    is_verified_guide: bool
    streak_days: int
    total_habits_completed: int
    connection_count: int
    last_active_at: datetime


# Guide Application schemas
class GuideApplicationCreate(BaseSchema):
    """Schema for submitting Guide application."""
    motivation: str = Field(..., min_length=50, max_length=2000)
    expertise_areas: str = Field(..., min_length=10, max_length=500)
    relevant_experience: str = Field(..., min_length=50, max_length=2000)


class GuideApplicationResponse(BaseSchema, IDMixin, TimestampMixin):
    """Guide application response."""
    user_id: UUID
    motivation: str
    expertise_areas: str
    relevant_experience: str
    status: ApplicationStatus
    reviewed_by_guardian_id: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None


class GuideApplicationReview(BaseSchema):
    """Schema for Guardian reviewing Guide application."""
    status: ApplicationStatus
    review_notes: Optional[str] = None


# Trust Verification Application schemas
class TrustVerificationApplicationCreate(BaseSchema):
    """Schema for submitting trust verification application."""
    contributions_summary: str = Field(..., min_length=50, max_length=1000)
    why_good_soil: str = Field(..., min_length=50, max_length=1000)
    requested_level: TrustLevel


class TrustVerificationApplicationResponse(BaseSchema, IDMixin, TimestampMixin):
    """Trust verification application response."""
    user_id: UUID
    contributions_summary: str
    why_good_soil: str
    requested_level: TrustLevel
    status: ApplicationStatus
    reviewed_by_guardian_id: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None


class TrustVerificationReview(BaseSchema):
    """Schema for Guardian reviewing trust application."""
    status: ApplicationStatus
    review_notes: Optional[str] = None
