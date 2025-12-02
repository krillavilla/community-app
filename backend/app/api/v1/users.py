"""
User and authentication API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user's profile.
    
    Returns full user profile with stats and settings.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    Allows updating display_name, bio, avatar_url, and spiritual_opt_in.
    """
    # TODO: Validate avatar_url format
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get another user's public profile.
    
    Returns public profile information only.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


class AgeVerificationRequest(BaseModel):
    date_of_birth: str  # YYYY-MM-DD format


@router.post("/me/verify-age")
async def verify_age(
    age_data: AgeVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify user's age (required before posting video content)
    
    Users must be at least 13 years old to use Garden.
    Users under 18 have additional safety restrictions.
    """
    try:
        dob = date.fromisoformat(age_data.date_of_birth)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Calculate age
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    # COPPA compliance - minimum age 13
    if age < 13:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be at least 13 years old to use Garden"
        )
    
    # Update user
    current_user.date_of_birth = dob
    current_user.age_verified = True
    db.commit()
    
    return {
        "message": "Age verified successfully",
        "is_minor": age < 18,
        "age_verified": True
    }
