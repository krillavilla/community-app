"""
Soil model - Comments as nutrients with voting.

Soil represents comments in the Garden System. They have nutrient scores
(nitrogen - toxin) that affect seed lifespan and vine reputation.
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, Text, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Soil(Base):
    """
    Soil model - represents comments as nutrients.
    
    Soil nourishes or poisons seeds based on voting.
    Positive votes = nitrogen (extends lifespan +6 hours)
    Negative votes = toxins (reduces lifespan, 5+ toxins = instant delete)
    """
    __tablename__ = "soil"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    seed_id = Column(UUID(as_uuid=True), ForeignKey("seeds.id", ondelete="CASCADE"), nullable=False)
    vine_id = Column(UUID(as_uuid=True), ForeignKey("vines.id", ondelete="CASCADE"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    
    # Nutrient value (net: nitrogen - toxins)
    nutrient_score = Column(Integer, nullable=False, default=0)     # Net score
    nitrogen_count = Column(Integer, nullable=False, default=0)     # Upvotes
    toxin_count = Column(Integer, nullable=False, default=0)        # Downvotes
    
    # Lifecycle
    added_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    decays_at = Column(DateTime, nullable=True)      # When comment expires
    composted_at = Column(DateTime, nullable=True)   # When archived
    soft_deleted = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    # seed = relationship("Seed", back_populates="soil_comments")
    # vine = relationship("Vine", back_populates="soil_comments")
    # nutrients = relationship("Nutrient", back_populates="soil")
    
    @property
    def is_toxic(self) -> bool:
        """Check if comment has excessive toxins (5+ downvotes)."""
        return self.toxin_count >= 5
    
    @property
    def is_nourishing(self) -> bool:
        """Check if comment has positive nutrient score."""
        return self.nutrient_score > 0
    
    @property
    def time_until_decay(self) -> timedelta | None:
        """Calculate remaining time before decay."""
        if not self.decays_at:
            return None
        return self.decays_at - datetime.utcnow()
    
    def add_nitrogen(self):
        """
        Add nitrogen (upvote) to soil.
        
        Increases nutrient score and extends parent seed lifespan by 6 hours.
        """
        self.nitrogen_count += 1
        self.nutrient_score = self.nitrogen_count - self.toxin_count
    
    def add_toxin(self):
        """
        Add toxin (downvote) to soil.
        
        Decreases nutrient score. If toxin_count >= 5, marks for immediate deletion.
        """
        self.toxin_count += 1
        self.nutrient_score = self.nitrogen_count - self.toxin_count
        
        # Mark for deletion if too toxic
        if self.is_toxic:
            self.soft_deleted = True
    
    def remove_nitrogen(self):
        """Remove nitrogen (undo upvote)."""
        if self.nitrogen_count > 0:
            self.nitrogen_count -= 1
            self.nutrient_score = self.nitrogen_count - self.toxin_count
    
    def remove_toxin(self):
        """Remove toxin (undo downvote)."""
        if self.toxin_count > 0:
            self.toxin_count -= 1
            self.nutrient_score = self.nitrogen_count - self.toxin_count
            
            # Restore if no longer toxic
            if not self.is_toxic:
                self.soft_deleted = False
    
    def __repr__(self):
        return f"<Soil {self.id} on seed {self.seed_id} - score {self.nutrient_score}>"
