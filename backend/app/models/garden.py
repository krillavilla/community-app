"""
My Garden feature models.

Personal habit tracking with categories, frequencies, and progress logs.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class HabitCategory(str, enum.Enum):
    """Habit categories for organization."""
    PHYSICAL = "physical"
    MENTAL = "mental"
    SPIRITUAL = "spiritual"
    SOCIAL = "social"
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    OTHER = "other"


class HabitFrequency(str, enum.Enum):
    """How often a habit should be completed."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class Garden(Base):
    """
    User's personal habit garden.
    
    Each user has one Garden containing their habits and progress.
    """
    __tablename__ = "gardens"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Garden metadata
    name = Column(String(100), default="My Garden", nullable=False)
    description = Column(Text, nullable=True)
    
    # Privacy
    is_public = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="garden")
    habits = relationship("Habit", back_populates="garden", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Garden {self.name} for User {self.user_id}>"


class Habit(Base):
    """
    Individual habit within a Garden.
    
    Tracks habit details, frequency, and target metrics.
    """
    __tablename__ = "habits"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to Garden
    garden_id = Column(UUID(as_uuid=True), ForeignKey("gardens.id"), nullable=False)
    
    # Habit details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(SQLEnum(HabitCategory), nullable=False, default=HabitCategory.OTHER)
    
    # Frequency and goals
    frequency = Column(SQLEnum(HabitFrequency), nullable=False, default=HabitFrequency.DAILY)
    target_count = Column(Integer, default=1, nullable=False)  # e.g., 3 times per week
    
    # Reminders
    reminder_time = Column(String(10), nullable=True)  # HH:MM format
    reminder_enabled = Column(Boolean, default=False, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    garden = relationship("Garden", back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Habit {self.name} ({self.frequency})>"


class HabitLog(Base):
    """
    Individual log entry for habit completion.
    
    Records when a habit was completed and optional notes.
    """
    __tablename__ = "habit_logs"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to Habit
    habit_id = Column(UUID(as_uuid=True), ForeignKey("habits.id"), nullable=False)
    
    # Completion details
    completed_at = Column(Date, nullable=False)  # Date of completion
    notes = Column(Text, nullable=True)
    
    # Optional metrics
    duration_minutes = Column(Integer, nullable=True)  # For timed activities
    quantity = Column(Integer, nullable=True)  # For countable activities
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    habit = relationship("Habit", back_populates="logs")
    
    def __repr__(self):
        return f"<HabitLog for Habit {self.habit_id} on {self.completed_at}>"
