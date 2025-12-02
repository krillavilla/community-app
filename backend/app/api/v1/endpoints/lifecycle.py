from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user
from app.models.seed import Seed, LifecycleStage
from pydantic import BaseModel
from datetime import datetime
router = APIRouter()
class LifecycleResponse(BaseModel):
    stage: str
    emoji: str
    updated_at: datetime
    engagement_score: int
    progress_to_next: float
@router.get("/seeds/{seed_id}/lifecycle")
def get_seed_lifecycle(seed_id: str, db: Session = Depends(get_db)):
    """Get lifecycle info for a seed"""
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    if not seed:
        raise HTTPException(404, "Seed not found")

    # Calculate progress (score needed for next stage)
    score = seed.engagement_score
    progress = min((score / 20) * 100, 100)  # 20 = vine threshold

    return LifecycleResponse(
        stage=seed.lifecycle_stage.value,
        emoji=seed.lifecycle_emoji,
        updated_at=seed.lifecycle_updated_at,
        engagement_score=score,
        progress_to_next=progress
    )
@router.post("/seeds/{seed_id}/water")
def water_seed(
    seed_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """'Water' a seed - add engagement"""
    seed = db.query(Seed).filter(Seed.id == seed_id).first()
    if not seed:
        raise HTTPException(404, "Seed not found")

    # Increment water level (views)
    seed.add_water(1)
    seed.engagement_score = seed.calculate_engagement_score()
    db.commit()

    return {"message": "💧 Seed watered!", "new_score": seed.engagement_score}
