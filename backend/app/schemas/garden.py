"""
Pydantic schemas for Garden System API.

Request and response models for seeds, vines, soil, and gardens.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


# Seed Schemas
class SeedCreate(BaseModel):
    """Request to plant a seed (create post)."""
    content: Optional[str] = Field(None, max_length=5000, description="Caption text")
    privacy_fence: str = Field("public", description="Privacy level: public, friends, close_friends, orchard, private")


class SeedResponse(BaseModel):
    """Seed response with full details."""
    id: UUID
    vine_id: UUID
    content: Optional[str]
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    mux_playback_id: Optional[str]
    
    # Lifecycle
    state: str
    planted_at: datetime
    sprouts_at: Optional[datetime]
    wilts_at: Optional[datetime]
    composted_at: Optional[datetime]
    
    # Growth metrics
    water_level: int
    nutrient_score: int
    sunlight_hours: int
    
    # Garden location
    garden_type: str
    privacy_fence: str
    soil_health: float
    
    # Computed
    time_until_wilt: Optional[str] = None  # Human-readable
    growth_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class SeedSummary(BaseModel):
    """Minimal seed info for feeds."""
    id: UUID
    vine_id: UUID
    content: Optional[str]
    mux_playback_id: Optional[str]
    thumbnail_url: Optional[str]
    state: str
    water_level: int
    nutrient_score: int
    sunlight_hours: int
    planted_at: datetime
    wilts_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Vine Schemas
class VineResponse(BaseModel):
    """Vine profile response."""
    id: UUID
    user_id: UUID
    
    # Health
    root_strength: float
    soil_health: float
    growth_stage: str
    
    # Activity
    planted_at: datetime
    last_watered_at: datetime
    selected_paths: Optional[List[str]]
    
    # Stats
    seeds_planted: int
    soil_given: int
    sunlight_received: int
    
    # Computed
    days_since_planted: Optional[int] = None
    needs_water: Optional[bool] = None
    reputation_score: Optional[float] = None
    
    class Config:
        from_attributes = True


# Soil Schemas
class SoilCreate(BaseModel):
    """Request to add soil (comment)."""
    content: str = Field(..., min_length=1, max_length=2000, description="Comment text")


class SoilResponse(BaseModel):
    """Soil response with full details."""
    id: UUID
    seed_id: UUID
    vine_id: UUID
    content: str
    
    # Nutrients
    nutrient_score: int
    nitrogen_count: int
    toxin_count: int
    
    # Lifecycle
    added_at: datetime
    decays_at: Optional[datetime]
    composted_at: Optional[datetime]
    
    # Computed
    is_toxic: Optional[bool] = None
    is_nourishing: Optional[bool] = None
    
    class Config:
        from_attributes = True


# Feed Schemas
class FeedRequest(BaseModel):
    """Request for feed data."""
    skip: int = Field(0, ge=0, description="Pagination offset")
    limit: int = Field(20, ge=1, le=100, description="Max results")


class FeedResponse(BaseModel):
    """Feed response with seeds."""
    seeds: List[SeedSummary]
    total: Optional[int] = None
    has_more: bool = False


# Action Schemas
class WaterResponse(BaseModel):
    """Response after watering seed."""
    seed_id: UUID
    water_level: int
    message: str = "Seed watered"


class SunlightResponse(BaseModel):
    """Response after shining sunlight."""
    seed_id: UUID
    sunlight_hours: int
    message: str = "Sunlight added"


class VoteResponse(BaseModel):
    """Response after voting on soil."""
    soil_id: UUID
    vote_type: str  # "nitrogen" or "toxin"
    nutrient_score: int
    message: str


# Search Schemas
class SearchRequest(BaseModel):
    """Request for seed search."""
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    skip: int = Field(0, ge=0, description="Pagination offset")
    limit: int = Field(20, ge=1, le=100, description="Max results")


# Climate Schemas
class ClimateReadingResponse(BaseModel):
    """Climate reading response."""
    id: UUID
    measured_at: datetime
    toxicity_level: float
    growth_rate: float
    drought_risk: float
    pest_incidents: int
    temperature: float
    
    # Computed
    health_score: Optional[float] = None
    is_healthy: Optional[bool] = None
    needs_intervention: Optional[bool] = None
    
    class Config:
        from_attributes = True
