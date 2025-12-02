"""
Gardens API - Feed endpoints for Wild Garden, Garden Rows, Greenhouse.

Handles:
- GET /gardens/wild - Wild Garden (For You Page)
- GET /gardens/rows - Garden Rows (Following)
- GET /gardens/greenhouse - Greenhouse (Private)
- GET /gardens/search - Search seeds
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.user import User
from app.models.vine import Vine
from app.schemas.garden import FeedResponse, SeedSummary
from app.garden.feeds import GardenFeedService


router = APIRouter()


@router.get("/wild", response_model=FeedResponse)
def get_wild_garden(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Wild Garden feed (For You Page).
    
    Algorithm-driven feed prioritizing:
    - Blooming seeds (active growth)
    - High growth scores
    - Freshness
    - Diversity
    - Avoiding recently seen seeds
    """
    # Get vine for current user
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        # Create vine for new user
        vine = Vine(user_id=current_user.id)
        db.add(vine)
        db.commit()
        db.refresh(vine)
    
    # Get feed
    feed_service = GardenFeedService(db)
    seeds = feed_service.get_wild_garden(str(vine.id), skip, limit)
    
    # Convert to summaries
    seed_summaries = [SeedSummary.from_orm(seed) for seed in seeds]
    
    return FeedResponse(
        seeds=seed_summaries,
        has_more=len(seeds) == limit
    )


@router.get("/rows", response_model=FeedResponse)
def get_garden_rows(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Garden Rows feed (Following).
    
    Chronological feed of seeds from connections.
    """
    # Get vine for current user
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        raise HTTPException(404, "Vine not found")
    
    # Get feed
    feed_service = GardenFeedService(db)
    seeds = feed_service.get_garden_rows(str(vine.id), skip, limit)
    
    # Convert to summaries
    seed_summaries = [SeedSummary.from_orm(seed) for seed in seeds]
    
    return FeedResponse(
        seeds=seed_summaries,
        has_more=len(seeds) == limit
    )


@router.get("/greenhouse", response_model=FeedResponse)
def get_greenhouse(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Greenhouse feed (Private).
    
    User's own seeds (all states except composting).
    """
    # Get vine for current user
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        raise HTTPException(404, "Vine not found")
    
    # Get feed
    feed_service = GardenFeedService(db)
    seeds = feed_service.get_greenhouse(str(vine.id), skip, limit)
    
    # Convert to summaries
    seed_summaries = [SeedSummary.from_orm(seed) for seed in seeds]
    
    return FeedResponse(
        seeds=seed_summaries,
        has_more=len(seeds) == limit
    )


@router.get("/search", response_model=FeedResponse)
def search_seeds(
    query: str = Query(..., min_length=1, max_length=100, description="Search query"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search seeds by content.
    
    Simple text search across seed content.
    """
    # Get vine for current user
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        raise HTTPException(404, "Vine not found")
    
    # Search
    feed_service = GardenFeedService(db)
    seeds = feed_service.search_seeds(query, str(vine.id), skip, limit)
    
    # Convert to summaries
    seed_summaries = [SeedSummary.from_orm(seed) for seed in seeds]
    
    return FeedResponse(
        seeds=seed_summaries,
        has_more=len(seeds) == limit
    )
