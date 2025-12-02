"""
Seed model - Posts/Videos with lifecycle management.

Seeds represent content in the Garden System. They have lifecycle states
(planted → sprouting → blooming → wilting → composting) and growth metrics.
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class SeedState(str, enum.Enum):
    """Lifecycle states for seeds."""
    planted = "planted"       # Just created, processing video
    sprouting = "sprouting"   # Video ready, gaining initial traction
    blooming = "blooming"     # Actively getting engagement
    wilting = "wilting"       # Approaching expiration
    composting = "composting" # Expired, being archived


class LifecycleStage(str, enum.Enum):
    """New lifecycle stages for Garden System B2."""
    SEED = "seed"          # 🌱 Initial stage (0-24h)
    SPROUT = "sprout"      # 🌿 Gaining traction (5+ engagements)
    VINE = "vine"          # 🍇 High resonance (20+ engagements)
    FRUIT = "fruit"        # 🍂 Mature content (30+ days)
    COMPOST = "compost"    # 💀 Expired, ML learns from it


class GardenType(str, enum.Enum):
    """Types of gardens where seeds can appear."""
    WILD = "wild"           # For You Page (FYP) - algorithm-driven
    ROWS = "rows"           # Following feed - chronological
    GREENHOUSE = "greenhouse"  # Private/saved content


class FenceType(str, enum.Enum):
    """Privacy levels for seeds."""
    PUBLIC = "public"              # Everyone can see
    FRIENDS = "friends"            # Connections only
    CLOSE_FRIENDS = "close_friends"  # Inner circle
    ORCHARD = "orchard"            # Specific community
    PRIVATE = "private"            # Only creator


class Seed(Base):
    """
    Seed model - represents posts/videos with lifecycle.
    
    Seeds grow through lifecycle states and have growth metrics
    (water, nutrients, sunlight) that affect their visibility and lifespan.
    """
    __tablename__ = "seeds"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to User (vine_id in garden metaphor)
    vine_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Content
    content = Column(Text, nullable=True)
    video_url = Column(String(512), nullable=True)
    thumbnail_url = Column(String(512), nullable=True)
    mux_asset_id = Column(String(255), nullable=True)
    mux_playback_id = Column(String(255), nullable=True)
    
    # Lifecycle state (original system)
    state = Column(SQLEnum(SeedState), nullable=False, default=SeedState.planted)
    planted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sprouts_at = Column(DateTime, nullable=True)  # When it becomes visible
    wilts_at = Column(DateTime, nullable=True)    # Expiration time
    composted_at = Column(DateTime, nullable=True)  # When archived
    
    # New lifecycle engine (B2 system)
    lifecycle_stage = Column(SQLEnum(LifecycleStage, values_callable=lambda x: [e.value for e in x]), nullable=False, default=LifecycleStage.SEED)
    lifecycle_updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    engagement_score = Column(Integer, nullable=False, default=0)
    expiry_date = Column(DateTime, nullable=True)
    
    # Growth metrics
    water_level = Column(Integer, nullable=False, default=0)      # Views
    nutrient_score = Column(Integer, nullable=False, default=0)   # Net comment votes
    sunlight_hours = Column(Integer, nullable=False, default=0)   # Shares
    
    # Garden location
    garden_type = Column(SQLEnum(GardenType), nullable=False, default=GardenType.WILD)
    privacy_fence = Column(SQLEnum(FenceType), nullable=False, default=FenceType.PUBLIC)
    
    # Soil data
    soil_health = Column(Float, nullable=False, default=1.0)  # Toxicity multiplier
    pollination_vector = Column(ARRAY(Float), nullable=True)  # ML embedding for similarity
    
    # Soft delete
    soft_deleted = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    # TODO: Add relationship to User (vine)
    # soil_comments = relationship("Soil", back_populates="seed")
    # pollination_events = relationship("PollinationEvent", back_populates="seed")
    
    @property
    def is_blooming(self) -> bool:
        """Check if seed is in active growth state."""
        return self.state == SeedState.blooming
    
    @property
    def time_until_wilt(self) -> timedelta | None:
        """Calculate remaining time before wilting."""
        if not self.wilts_at:
            return None
        return self.wilts_at - datetime.utcnow()
    
    @property
    def growth_score(self) -> float:
        """
        Calculate overall growth score.
        
        Formula: (water * 0.3) + (nutrients * 0.5) + (sunlight * 0.2)
        Nutrients weighted highest as comment quality matters most.
        """
        return (
            (self.water_level * 0.3) +
            (self.nutrient_score * 0.5) +
            (self.sunlight_hours * 0.2)
        )
    
    def add_water(self, amount: int = 1):
        """Add water (view) to seed."""
        self.water_level += amount
    
    def add_sunlight(self, hours: int = 1):
        """Add sunlight (share) to seed."""
        self.sunlight_hours += hours
    
    def extend_lifespan(self, hours: int):
        """
        Extend seed lifespan by adding hours.
        
        Called when receiving positive nutrients (upvoted comments).
        Max lifespan: 30 days from planted_at.
        """
        if not self.wilts_at:
            self.wilts_at = datetime.utcnow() + timedelta(hours=hours)
        else:
            new_wilts_at = self.wilts_at + timedelta(hours=hours)
            max_wilts_at = self.planted_at + timedelta(days=30)
            self.wilts_at = min(new_wilts_at, max_wilts_at)
    
    def reduce_lifespan(self, hours: int):
        """
        Reduce seed lifespan.
        
        Called when receiving toxins (downvoted comments).
        Min: immediate wilting.
        """
        if not self.wilts_at:
            self.wilts_at = datetime.utcnow()
        else:
            new_wilts_at = self.wilts_at - timedelta(hours=hours)
            self.wilts_at = max(new_wilts_at, datetime.utcnow())
    
    # ===== B2 LIFECYCLE ENGINE METHODS =====
    
    @property
    def lifecycle_emoji(self) -> str:
        """Return emoji for current lifecycle stage."""
        emoji_map = {
            LifecycleStage.SEED: "🌱",
            LifecycleStage.SPROUT: "🌿",
            LifecycleStage.VINE: "🍇",
            LifecycleStage.FRUIT: "🍂",
            LifecycleStage.COMPOST: "💀"
        }
        return emoji_map.get(self.lifecycle_stage, "🌱")
    
    def calculate_engagement_score(self) -> int:
        """
        Calculate total engagement score.
        
        Uses water (views), nutrients (comments), sunlight (shares).
        Weighted to prioritize shares and comments over views.
        """
        score = (
            (self.water_level or 0) +
            (self.nutrient_score or 0) * 2 +
            (self.sunlight_hours or 0) * 5
        )
        return score
    
    def update_lifecycle_stage(self) -> LifecycleStage:
        """
        Determine if seed should transition to next stage.
        
        Returns new stage based on engagement + age.
        Worker calls this to check transitions.
        """
        score = self.calculate_engagement_score()
        age_hours = (datetime.utcnow() - self.planted_at).total_seconds() / 3600
        
        # Transition rules (most specific first)
        if age_hours >= 720:  # 30 days
            return LifecycleStage.FRUIT
        elif score >= 20 and age_hours >= 24:
            return LifecycleStage.VINE
        elif score >= 5 and age_hours >= 1:
            return LifecycleStage.SPROUT
        
        return self.lifecycle_stage
    
    def __repr__(self):
        return f"<Seed {self.id} {self.lifecycle_emoji} - {self.lifecycle_stage} by vine {self.vine_id}>"
