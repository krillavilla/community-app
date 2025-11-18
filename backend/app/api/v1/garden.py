"""
My Garden habit tracking API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps.db import get_db
from app.api.deps.auth import get_current_user
from app.models.user import User
from app.models.garden import Garden, Habit, HabitLog
from app.schemas.garden import (
    HabitCreate,
    HabitUpdate,
    HabitResponse,
    HabitLogCreate,
    HabitLogResponse,
    GardenResponse
)

router = APIRouter(prefix="/garden", tags=["garden"])


@router.get("/", response_model=GardenResponse)
async def get_my_garden(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's Garden with all habits.
    
    Creates Garden if it doesn't exist.
    """
    garden = db.query(Garden).filter(Garden.user_id == current_user.id).first()
    
    if not garden:
        # Create garden on first access
        garden = Garden(user_id=current_user.id, name="My Garden")
        db.add(garden)
        db.commit()
        db.refresh(garden)
    
    return garden


@router.post("/habits", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit(
    habit_data: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new habit in user's Garden.
    
    TODO: Validate reminder_time format
    """
    # Get or create garden
    garden = db.query(Garden).filter(Garden.user_id == current_user.id).first()
    if not garden:
        garden = Garden(user_id=current_user.id, name="My Garden")
        db.add(garden)
        db.commit()
        db.refresh(garden)
    
    # Create habit
    habit = Habit(**habit_data.model_dump(), garden_id=garden.id)
    db.add(habit)
    db.commit()
    db.refresh(habit)
    
    return habit


@router.get("/habits/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific habit by ID."""
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Verify ownership
    garden = db.query(Garden).filter(Garden.id == habit.garden_id).first()
    if garden.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this habit"
        )
    
    return habit


@router.put("/habits/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: str,
    habit_update: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a habit."""
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Verify ownership
    garden = db.query(Garden).filter(Garden.id == habit.garden_id).first()
    if garden.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this habit"
        )
    
    # Update fields
    update_data = habit_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)
    
    db.commit()
    db.refresh(habit)
    
    return habit


@router.delete("/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a habit (soft delete by setting is_active=False)."""
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Verify ownership
    garden = db.query(Garden).filter(Garden.id == habit.garden_id).first()
    if garden.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this habit"
        )
    
    # Soft delete
    habit.is_active = False
    db.commit()
    
    return None


@router.post("/habits/{habit_id}/logs", response_model=HabitLogResponse, status_code=status.HTTP_201_CREATED)
async def log_habit_completion(
    habit_id: str,
    log_data: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log a habit completion.
    
    TODO: Update user's streak and total_habits_completed
    """
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    
    # Verify ownership
    garden = db.query(Garden).filter(Garden.id == habit.garden_id).first()
    if garden.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to log this habit"
        )
    
    # Create log
    habit_log = HabitLog(**log_data.model_dump(), habit_id=habit.id)
    db.add(habit_log)
    db.commit()
    db.refresh(habit_log)
    
    return habit_log
