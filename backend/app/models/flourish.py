"""
Flourish Feed feature models.

Community posts with comments and reactions.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class PostType(str, enum.Enum):
    """Type of Flourish post."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    POLL = "poll"
    MILESTONE = "milestone"


class PostVisibility(str, enum.Enum):
    """Post visibility settings."""
    PUBLIC = "public"
    CONNECTIONS_ONLY = "connections_only"
    GOOD_SOIL_PLUS = "good_soil_plus"  # Only Good Soil and Flourishing users


class ReactionType(str, enum.Enum):
    """Reaction types for posts and comments."""
    HEART = "heart"
    SUPPORT = "support"
    CELEBRATE = "celebrate"
    INSIGHTFUL = "insightful"
    PRAYER = "prayer"  # For spiritual_opt_in users


class FlourishPost(Base):
    """
    Community post in Flourish Feed.
    
    Supports text, images, videos, polls, and milestone celebrations.
    """
    __tablename__ = "flourish_posts"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to User (author)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Content
    post_type = Column(SQLEnum(PostType), nullable=False, default=PostType.TEXT)
    content = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)  # Image/video URL
    
    # Privacy and visibility
    visibility = Column(SQLEnum(PostVisibility), nullable=False, default=PostVisibility.PUBLIC)
    is_spiritual = Column(Boolean, default=False, nullable=False)
    
    # Moderation
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    
    # Engagement metrics (TODO: compute from relationships)
    reaction_count = Column(Integer, default=0, nullable=False)
    comment_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    author = relationship("User", backref="flourish_posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="post", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FlourishPost {self.id} by User {self.author_id}>"


class Comment(Base):
    """
    Comment on a Flourish post.
    
    Supports nested replies via parent_comment_id.
    """
    __tablename__ = "comments"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    post_id = Column(UUID(as_uuid=True), ForeignKey("flourish_posts.id"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=True)
    
    # Content
    content = Column(Text, nullable=False)
    
    # Moderation
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    
    # Engagement
    reaction_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    post = relationship("FlourishPost", back_populates="comments")
    author = relationship("User", backref="comments")
    parent_comment = relationship("Comment", remote_side=[id], backref="replies")
    reactions = relationship("Reaction", back_populates="comment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Comment {self.id} by User {self.author_id}>"


class Reaction(Base):
    """
    Reaction to a post or comment.
    
    One reaction per user per post/comment (enforced by unique constraints).
    """
    __tablename__ = "reactions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys (mutually exclusive: either post_id OR comment_id)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    post_id = Column(UUID(as_uuid=True), ForeignKey("flourish_posts.id"), nullable=True)
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=True)
    
    # Reaction type
    reaction_type = Column(SQLEnum(ReactionType), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="reactions")
    post = relationship("FlourishPost", back_populates="reactions")
    comment = relationship("Comment", back_populates="reactions")
    
    def __repr__(self):
        return f"<Reaction {self.reaction_type} by User {self.user_id}>"
