"""
Base Pydantic schemas with common patterns.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common config."""
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    """Mixin for UUID primary key."""
    id: UUID


class PaginationParams(BaseModel):
    """Query parameters for pagination."""
    skip: int = 0
    limit: int = 20


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: list
    total: int
    skip: int
    limit: int
    has_more: bool
