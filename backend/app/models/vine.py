"""
Vine model - Users with garden health metrics.

Vines represent users in the Garden System. They have health metrics
(root_strength, soil_health), growth stages, and activity tracking.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class VineGrowth(str, enum.Enum):
    """Growth stages for vines (users)."""
    SEEDLING = "seedling"  # New user (0-30 days)
    VINE = "vine"          # Active user (30-180 days)
    MATURE = "mature"      # Established user (180-365 days)
    ANCIENT = "ancient"    # Veteran user (365+ days)


class Vine(Base):
    """
    Vine model - represents users with garden health metrics.
    
    Vines grow over time, track activity, and have health metrics
    that affect their reputation and reach in the community.
    """
    __tablename__ = "vines"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to User (one-to-one)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Vine health metrics
    root_strength = Column(Float, nullable=False, default=0.5)  # Connection quality (0-1)
    soil_health = Column(Float, nullable=False, default=1.0)    # Reputation multiplier (0-2)
    growth_stage = Column(SQLEnum(VineGrowth), nullable=False, default=VineGrowth.SEEDLING)
    
    # Activity tracking
    planted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_watered_at = Column(DateTime, nullable=False, default=datetime.utcnow)  # Last activity
    
    # Growth paths (JSON array: ['personal', 'emotional', 'spiritual', 'social'])
    selected_paths = Column(JSONB, nullable=True)
    
    # Stats
    seeds_planted = Column(Integer, nullable=False, default=0)      # Posts created
    soil_given = Column(Integer, nullable=False, default=0)         # Comments made
    sunlight_received = Column(Integer, nullable=False, default=0)  # Total engagement received
    
    # Relationships
    # user = relationship("User", back_populates="vine")
    # seeds = relationship("Seed", back_populates="vine")
    # soil_comments = relationship("Soil", back_populates="vine")
    # fences = relationship("Fence", foreign_keys="Fence.vine_id", back_populates="vine")
    
    @property
    def days_since_planted(self) -> int:
        """Calculate days since vine was planted."""
        return (datetime.utcnow() - self.planted_at).days
    
    @property
    def needs_water(self) -> bool:
        """Check if vine needs watering (inactive for 7+ days)."""
        days_since_water = (datetime.utcnow() - self.last_watered_at).days
        return days_since_water >= 7
    
    @property
    def is_healthy(self) -> bool:
        """Check if vine is in good health (soil_health >= 0.8)."""
        return self.soil_health >= 0.8
    
    @property
    def reputation_score(self) -> float:
        """
        Calculate overall reputation score.
        
        Based on soil_health and root_strength.
        Range: 0-100
        """
        return (self.soil_health * 60) + (self.root_strength * 40)
    
    def water(self):
        """Update last watered timestamp (activity)."""
        self.last_watered_at = datetime.utcnow()
    
    def update_growth_stage(self):
        """
        Update growth stage based on days since planted.
        
        Seedling: 0-30 days
        Vine: 30-180 days
        Mature: 180-365 days
        Ancient: 365+ days
        """
        days = self.days_since_planted
        if days < 30:
            self.growth_stage = VineGrowth.SEEDLING
        elif days < 180:
            self.growth_stage = VineGrowth.VINE
        elif days < 365:
            self.growth_stage = VineGrowth.MATURE
        else:
            self.growth_stage = VineGrowth.ANCIENT
    
    def adjust_soil_health(self, delta: float):
        """
        Adjust soil health by delta.
        
        Soil health affects content reach and community standing.
        Clamped between 0.0 and 2.0.
        """
        self.soil_health = max(0.0, min(2.0, self.soil_health + delta))
    
    def adjust_root_strength(self, delta: float):
        """
        Adjust root strength by delta.
        
        Root strength represents connection quality.
        Clamped between 0.0 and 1.0.
        """
        self.root_strength = max(0.0, min(1.0, self.root_strength + delta))
    
    def plant_seed(self):
        """Increment seeds planted counter."""
        self.seeds_planted += 1
        self.water()
    
    def add_soil(self):
        """Increment soil given counter."""
        self.soil_given += 1
        self.water()
    
    def receive_sunlight(self, amount: int = 1):
        """Increment sunlight received counter."""
        self.sunlight_received += amount
    
    def __repr__(self):
        return f"<Vine {self.id} - {self.growth_stage} for user {self.user_id}>"
