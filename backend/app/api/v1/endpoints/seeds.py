"""
Seeds API - Endpoints for planting and managing seeds (posts/videos).

Handles:
- POST /seeds - Plant a seed (create post with video)
- GET /seeds/{id} - Get seed by ID
- POST /seeds/{id}/water - Record view
- POST /seeds/{id}/sunlight - Record share
- GET /seeds/{id}/soil - Get comments for seed
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.user import User
from app.models.seed import Seed, FenceType
from app.models.vine import Vine
from app.schemas.garden import (
    SeedCreate,
    SeedResponse,
    SoilResponse,
    WaterResponse,
    SunlightResponse
)
from app.garden.lifecycle import LifecycleEngine
from app.garden.soil_service import SoilService
from app.garden.feeds import GardenFeedService
from app.services.storage_service import StorageService
from app.services.mux_service import MuxService


router = APIRouter()


@router.post("/", response_model=SeedResponse, status_code=201)
async def plant_seed(
    file: UploadFile = File(...),
    content: Optional[str] = None,
    privacy_fence: str = "public",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Plant a seed (create post with video).
    
    Uploads video to R2, sends to Mux for encoding, creates seed in database.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(400, "File must be a video")
    
    # Read file
    file_data = await file.read()
    
    # Check size (100MB max)
    if len(file_data) > 100 * 1024 * 1024:
        raise HTTPException(400, "Video too large (max 100MB)")
    
    # Get or create vine for user
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        # Create vine for new user
        vine = Vine(user_id=current_user.id)
        db.add(vine)
        db.commit()
        db.refresh(vine)
    
    # Upload to R2
    storage = StorageService()
    video_url = storage.upload_video(file_data, file.filename)
    
    # Send to Mux for encoding
    mux_service = MuxService()
    mux_data = mux_service.create_asset(video_url)
    
    # Validate privacy fence
    try:
        fence_type = FenceType(privacy_fence)
    except ValueError:
        raise HTTPException(400, f"Invalid privacy_fence: {privacy_fence}")
    
    # Create seed
    seed = Seed(
        vine_id=vine.id,
        content=content,
        video_url=video_url,
        mux_asset_id=mux_data.get('asset_id'),
        mux_playback_id=mux_data.get('playback_id'),
        privacy_fence=fence_type
    )
    db.add(seed)
    
    # Update vine stats
    vine.plant_seed()
    
    db.commit()
    db.refresh(seed)
    
    # Add computed fields
    response = SeedResponse.from_orm(seed)
    response.growth_score = seed.growth_score
    if seed.time_until_wilt:
        hours = int(seed.time_until_wilt.total_seconds() / 3600)
        response.time_until_wilt = f"{hours} hours"
    
    return response


@router.get("/{seed_id}", response_model=SeedResponse)
def get_seed(
    seed_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get seed by ID with privacy check.
    """
    # Get vine for current user
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        raise HTTPException(404, "Vine not found")
    
    # Get seed with privacy check
    feed_service = GardenFeedService(db)
    seed = feed_service.get_seed_by_id(str(seed_id), str(vine.id))
    
    if not seed:
        raise HTTPException(404, "Seed not found or access denied")
    
    # Add computed fields
    response = SeedResponse.from_orm(seed)
    response.growth_score = seed.growth_score
    if seed.time_until_wilt:
        hours = int(seed.time_until_wilt.total_seconds() / 3600)
        response.time_until_wilt = f"{hours} hours"
    
    return response


@router.post("/{seed_id}/water", response_model=WaterResponse)
def water_seed(
    seed_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Water a seed (record view).
    """
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    if not seed:
        raise HTTPException(404, "Seed not found")
    
    # Water seed
    lifecycle = LifecycleEngine(db)
    lifecycle.water_seed(seed)
    
    return WaterResponse(
        seed_id=seed.id,
        water_level=seed.water_level
    )


@router.post("/{seed_id}/sunlight", response_model=SunlightResponse)
def shine_sunlight(
    seed_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Shine sunlight on seed (record share).
    """
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    if not seed:
        raise HTTPException(404, "Seed not found")
    
    # Add sunlight
    lifecycle = LifecycleEngine(db)
    lifecycle.shine_sunlight(seed)
    
    return SunlightResponse(
        seed_id=seed.id,
        sunlight_hours=seed.sunlight_hours
    )


@router.get("/{seed_id}/soil", response_model=list[SoilResponse])
def get_seed_soil(
    seed_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get soil (comments) for a seed.
    """
    # Check seed exists
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    if not seed:
        raise HTTPException(404, "Seed not found")
    
    # Get soil
    soil_service = SoilService(db)
    soil_list = soil_service.get_soil_for_seed(str(seed_id), skip, limit)
    
    # Add computed fields
    responses = []
    for soil in soil_list:
        resp = SoilResponse.from_orm(soil)
        resp.is_toxic = soil.is_toxic
        resp.is_nourishing = soil.is_nourishing
        responses.append(resp)
    
    return responses
