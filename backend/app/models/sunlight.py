"""
Share the Sunlight feature models.

Gratitude shares and win celebrations.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ShareType(str, enum.Enum):
    """Type of Sunlight share."""
    GRATITUDE = "gratitude"
    WIN = "win"
    MILESTONE = "milestone"
    REFLECTION = "reflection"


class SunlightReactionType(str, enum.Enum):
    """Reaction types for Sunlight posts."""
    SUNSHINE = "sunshine"
    CELEBRATE = "celebrate"
    GRATEFUL = "grateful"
    INSPIRED = "inspired"


class SunlightPost(Base):
    """
    Sunlight share post.
    
    Lightweight positive sharing for gratitude and wins.
    """
    __tablename__ = "sunlight_posts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to User (author)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Content
    share_type = Column(SQLEnum(ShareType), nullable=False)
    content = Column(Text, nullable=False)
    
    # Optional image
    image_url = Column(String(500), nullable=True)
    
    # Privacy
    is_spiritual = Column(Boolean, default=False, nullable=False)
    
    # Moderation
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    
    # Engagement metrics (TODO: compute from relationships)
    reaction_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    author = relationship("User", backref="sunlight_posts")
    reactions = relationship("SunlightReaction", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SunlightPost {self.id} ({self.share_type}) by User {self.author_id}>"


class SunlightReaction(Base):
    """
    Reaction to a Sunlight post.
    
    One reaction per user per post.
    """
    __tablename__ = "sunlight_reactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("sunlight_posts.id"), nullable=False)
    
    # Reaction type
    reaction_type = Column(SQLEnum(SunlightReactionType), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="sunlight_reactions")
    post = relationship("SunlightPost", back_populates="reactions")
    
    def __repr__(self):
        return f"<SunlightReaction {self.reaction_type} by User {self.user_id}>"
