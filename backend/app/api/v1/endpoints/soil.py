"""
Soil API - Endpoints for comments and voting.

Handles:
- POST /soil - Add soil (comment) to seed
- POST /soil/{id}/nitrogen - Upvote comment
- POST /soil/{id}/toxin - Downvote comment
- DELETE /soil/{id}/vote - Remove vote
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps.auth import get_current_user
from app.api.deps.db import get_db
from app.models.user import User
from app.models.vine import Vine
from app.models.seed import Seed
from app.schemas.garden import SoilCreate, SoilResponse, VoteResponse
from app.garden.soil_service import SoilService


router = APIRouter()


@router.post("/", response_model=SoilResponse, status_code=201)
def add_soil(
    seed_id: UUID,
    soil_data: SoilCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add soil (comment) to a seed.
    """
    # Get vine for current user
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        raise HTTPException(404, "Vine not found")
    
    # Check seed exists
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    if not seed:
        raise HTTPException(404, "Seed not found")
    
    # Add soil
    soil_service = SoilService(db)
    soil = soil_service.add_soil(str(seed_id), str(vine.id), soil_data.content)
    
    # Add computed fields
    response = SoilResponse.from_orm(soil)
    response.is_toxic = soil.is_toxic
    response.is_nourishing = soil.is_nourishing
    
    return response


@router.post("/{soil_id}/nitrogen", response_model=VoteResponse)
def add_nitrogen(
    soil_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add nitrogen (upvote) to soil.
    
    Extends parent seed lifespan by 6 hours per upvote.
    """
    # Get vine for current user
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        raise HTTPException(404, "Vine not found")
    
    # Add nitrogen
    soil_service = SoilService(db)
    try:
        nutrient = soil_service.add_nitrogen(str(soil_id), str(vine.id))
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    # Get updated soil
    from app.models.soil import Soil
    soil = db.query(Soil).filter(Soil.id == soil_id).first()
    
    return VoteResponse(
        soil_id=soil_id,
        vote_type="nitrogen",
        nutrient_score=soil.nutrient_score,
        message="Nitrogen added"
    )


@router.post("/{soil_id}/toxin", response_model=VoteResponse)
def add_toxin(
    soil_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add toxin (downvote) to soil.
    
    If soil reaches 5+ toxins, it's deleted and parent seed composted.
    """
    # Get vine for current user
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        raise HTTPException(404, "Vine not found")
    
    # Add toxin
    soil_service = SoilService(db)
    try:
        nutrient = soil_service.add_toxin(str(soil_id), str(vine.id))
    except ValueError as e:
        raise HTTPException(404, str(e))
    
    # Get updated soil
    from app.models.soil import Soil
    soil = db.query(Soil).filter(Soil.id == soil_id).first()
    
    if soil and soil.is_toxic:
        message = "Toxin added - soil deleted (5+ toxins)"
    else:
        message = "Toxin added"
    
    return VoteResponse(
        soil_id=soil_id,
        vote_type="toxin",
        nutrient_score=soil.nutrient_score if soil else 0,
        message=message
    )


@router.delete("/{soil_id}/vote")
def remove_vote(
    soil_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove vote from soil.
    """
    # Get vine for current user
    vine = db.query(Vine).filter(Vine.user_id == current_user.id).first()
    if not vine:
        raise HTTPException(404, "Vine not found")
    
    # Remove vote
    soil_service = SoilService(db)
    removed = soil_service.remove_vote(str(soil_id), str(vine.id))
    
    if not removed:
        raise HTTPException(404, "Vote not found")
    
    return {"message": "Vote removed"}
