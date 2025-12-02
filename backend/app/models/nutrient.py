"""
Nutrient model - Votes on soil (comments).

Nutrients represent individual votes on comments.
Nitrogen = upvote, Toxin = downvote.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class NutrientType(str, enum.Enum):
    """Types of nutrients."""
    NITROGEN = "nitrogen"  # Upvote
    TOXIN = "toxin"        # Downvote


class Nutrient(Base):
    """
    Nutrient model - represents votes on soil (comments).
    
    Each nutrient is a single vote by a vine on a soil comment.
    One vine can only vote once per soil (enforced by unique constraint).
    """
    __tablename__ = "nutrients"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    soil_id = Column(UUID(as_uuid=True), ForeignKey("soil.id", ondelete="CASCADE"), nullable=False)
    vine_id = Column(UUID(as_uuid=True), ForeignKey("vines.id", ondelete="CASCADE"), nullable=False)
    
    # Vote type
    type = Column(SQLEnum(NutrientType), nullable=False)
    strength = Column(Integer, nullable=False, default=1)  # Future: weighted voting
    
    # Timestamp
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    # soil = relationship("Soil", back_populates="nutrients")
    # vine = relationship("Vine")
    
    @property
    def is_nitrogen(self) -> bool:
        """Check if nutrient is nitrogen (upvote)."""
        return self.type == NutrientType.NITROGEN
    
    @property
    def is_toxin(self) -> bool:
        """Check if nutrient is toxin (downvote)."""
        return self.type == NutrientType.TOXIN
    
    def __repr__(self):
        return f"<Nutrient {self.type} by vine {self.vine_id} on soil {self.soil_id}>"
