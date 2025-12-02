"""
PollinationEvent model - Discovery tracking for seeds.

Pollination events track how vines discover seeds through different pathways.
Used for ML model training and discovery optimization.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class PollinationEvent(Base):
    """
    PollinationEvent model - tracks seed discovery.
    
    Records when and how a vine discovers a seed (via FYP, following, recommendations).
    Similarity scores from ML models guide pollination pathways.
    """
    __tablename__ = "pollination_events"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    seed_id = Column(UUID(as_uuid=True), ForeignKey("seeds.id", ondelete="CASCADE"), nullable=False)
    vine_id = Column(UUID(as_uuid=True), ForeignKey("vines.id", ondelete="CASCADE"), nullable=False)
    
    # Discovery pathway
    pathway = Column(String(50), nullable=False)  # 'wild_garden', 'rows', 'pollination', 'search'
    
    # ML similarity score (for pollination pathway)
    similarity_score = Column(Float, nullable=True)
    
    # Timestamp
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    # seed = relationship("Seed", back_populates="pollination_events")
    # vine = relationship("Vine")
    
    @property
    def is_pollination_discovery(self) -> bool:
        """Check if discovery was via ML-driven pollination."""
        return self.pathway == 'pollination'
    
    @property
    def is_organic_discovery(self) -> bool:
        """Check if discovery was via wild garden (FYP) or rows (following)."""
        return self.pathway in ['wild_garden', 'rows']
    
    def __repr__(self):
        return f"<PollinationEvent {self.pathway} - vine {self.vine_id} found seed {self.seed_id}>"
