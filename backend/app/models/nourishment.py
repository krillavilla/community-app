"""
Daily Nourishment feature models.

Curated inspirational content from Guardians.
"""
import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ContentType(str, enum.Enum):
    """Type of nourishment content."""
    QUOTE = "quote"
    REFLECTION = "reflection"
    PROMPT = "prompt"
    MEDITATION = "meditation"
    AFFIRMATION = "affirmation"


class ContentCategory(str, enum.Enum):
    """Category for content filtering."""
    SECULAR = "secular"
    SPIRITUAL = "spiritual"
    MIXED = "mixed"


class NourishmentItem(Base):
    """
    Daily inspirational content item.
    
    Curated by Guardians, scheduled for specific dates.
    """
    __tablename__ = "nourishment_items"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to Guardian who created it
    created_by_guardian_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    
    # Attribution
    author = Column(String(200), nullable=True)  # Original author (for quotes)
    source = Column(String(300), nullable=True)  # Book/source reference
    
    # Categorization
    category = Column(SQLEnum(ContentCategory), nullable=False, default=ContentCategory.SECULAR)
    tags = Column(Text, nullable=True)  # JSON array serialized as text
    
    # Scheduling
    scheduled_date = Column(Date, nullable=False, index=True)
    is_published = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    created_by = relationship("User", backref="nourishment_items_created")
    
    def __repr__(self):
        return f"<NourishmentItem '{self.title}' for {self.scheduled_date}>"
