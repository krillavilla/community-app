"""Garden habit tracking Pydantic schemas."""
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import Field
from app.models.garden import HabitCategory, HabitFrequency
from app.schemas.base import BaseSchema, IDMixin, TimestampMixin


class HabitCreate(BaseSchema):
    """Schema for creating a habit."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: HabitCategory
    frequency: HabitFrequency = HabitFrequency.DAILY
    target_count: int = Field(default=1, ge=1)
    reminder_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    reminder_enabled: bool = False


class HabitUpdate(BaseSchema):
    """Schema for updating a habit."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    category: Optional[HabitCategory] = None
    frequency: Optional[HabitFrequency] = None
    target_count: Optional[int] = Field(None, ge=1)
    reminder_time: Optional[str] = Field(None, pattern=r"^\d{2}:\d{2}$")
    reminder_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class HabitResponse(BaseSchema, IDMixin, TimestampMixin):
    """Habit response."""
    name: str
    description: Optional[str]
    category: HabitCategory
    frequency: HabitFrequency
    target_count: int
    reminder_time: Optional[str]
    reminder_enabled: bool
    is_active: bool


class HabitLogCreate(BaseSchema):
    """Schema for logging habit completion."""
    completed_at: date
    notes: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    quantity: Optional[int] = Field(None, ge=0)


class HabitLogResponse(BaseSchema, IDMixin):
    """Habit log response."""
    habit_id: UUID
    completed_at: date
    notes: Optional[str]
    duration_minutes: Optional[int]
    quantity: Optional[int]
    created_at: datetime


class GardenResponse(BaseSchema, IDMixin, TimestampMixin):
    """Garden response with habits."""
    user_id: UUID
    name: str
    description: Optional[str]
    is_public: bool
    habits: list[HabitResponse] = []
