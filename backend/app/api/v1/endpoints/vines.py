"""
Vines API - Endpoints for vine (user) profiles.

Handles:
- GET /vines/me - Get current user's vine profile
- GET /vines/{id} - Get vine by ID
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.user import User
from app.models.vine import Vine
from app.schemas.garden import VineResponse


router = APIRouter()


@router.get("/me", response_model=VineResponse)
def get_my_vine(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's vine profile.
    
    Creates vine if doesn't exist.
    """
    # Get or create vine
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        # Create vine for new user
        vine = Vine(user_id=current_user.id)
        db.add(vine)
        db.commit()
        db.refresh(vine)
    
    # Update growth stage
    vine.update_growth_stage()
    db.commit()
    
    # Add computed fields
    response = VineResponse.from_orm(vine)
    response.days_since_planted = vine.days_since_planted
    response.needs_water = vine.needs_water
    response.reputation_score = vine.reputation_score
    
    return response


@router.get("/{vine_id}", response_model=VineResponse)
def get_vine(
    vine_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get vine by ID.
    """
    vine = db.query(Vine).filter(Vine.id == vine_id).first()
    if not vine:
        raise HTTPException(404, "Vine not found")
    
    # Add computed fields
    response = VineResponse.from_orm(vine)
    response.days_since_planted = vine.days_since_planted
    response.needs_water = vine.needs_water
    response.reputation_score = vine.reputation_score
    
    return response
