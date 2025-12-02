"""
Root model - Direct messages between vines.

Roots represent DMs in the Garden System.
Messages can decay over time and be composted (archived).
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Root(Base):
    """
    Root model - represents direct messages.
    
    Roots connect vines through underground communication.
    Messages can have expiration times and be marked as read.
    """
    __tablename__ = "roots"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    from_vine_id = Column(UUID(as_uuid=True), ForeignKey("vines.id", ondelete="CASCADE"), nullable=False)
    to_vine_id = Column(UUID(as_uuid=True), ForeignKey("vines.id", ondelete="CASCADE"), nullable=False)
    
    # Content
    message = Column(Text, nullable=False)
    
    # Lifecycle
    decays_at = Column(DateTime, nullable=True)  # Expiration time
    composted = Column(Boolean, nullable=False, default=False)  # Archived
    is_read = Column(Boolean, nullable=False, default=False)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    # from_vine = relationship("Vine", foreign_keys=[from_vine_id])
    # to_vine = relationship("Vine", foreign_keys=[to_vine_id])
    
    @property
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if not self.decays_at:
            return False
        return datetime.utcnow() >= self.decays_at
    
    @property
    def time_until_decay(self) -> timedelta | None:
        """Calculate remaining time before decay."""
        if not self.decays_at:
            return None
        return self.decays_at - datetime.utcnow()
    
    def mark_read(self):
        """Mark message as read."""
        self.is_read = True
    
    def set_decay(self, hours: int):
        """Set message to decay after specified hours."""
        self.decays_at = datetime.utcnow() + timedelta(hours=hours)
    
    def compost(self):
        """Archive message."""
        self.composted = True
    
    def __repr__(self):
        return f"<Root from vine {self.from_vine_id} to {self.to_vine_id}>"
