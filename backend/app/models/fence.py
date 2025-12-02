"""
Fence model - Privacy circles for content visibility.

Fences control who can see seeds based on relationship types.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


# Import FenceType from seed.py to maintain consistency
class FenceType(str, enum.Enum):
    """Privacy levels for fences."""
    PUBLIC = "public"              # Everyone can see
    FRIENDS = "friends"            # Connections only
    CLOSE_FRIENDS = "close_friends"  # Inner circle
    ORCHARD = "orchard"            # Specific community
    PRIVATE = "private"            # Only creator


class Fence(Base):
    """
    Fence model - represents privacy circles.
    
    Fences define who can see seeds based on relationship types.
    Each fence entry grants a specific vine access at a specific level.
    """
    __tablename__ = "fences"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    vine_id = Column(UUID(as_uuid=True), ForeignKey("vines.id", ondelete="CASCADE"), nullable=False)  # Owner
    member_vine_id = Column(UUID(as_uuid=True), ForeignKey("vines.id", ondelete="CASCADE"), nullable=False)  # Member
    
    # Fence type
    fence_type = Column(SQLEnum(FenceType), nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    # vine = relationship("Vine", foreign_keys=[vine_id], back_populates="fences")
    # member = relationship("Vine", foreign_keys=[member_vine_id])
    
    def __repr__(self):
        return f"<Fence {self.fence_type} - vine {self.vine_id} includes {self.member_vine_id}>"
