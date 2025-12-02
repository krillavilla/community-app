"""
MVP Models - Simplified social features for user testing.

Garden metaphor kept symbolic:
- Posts = "seeds" (24hr lifespan)
- Likes = "watering"
- Comments = "soil"
- Privacy = public/friends only

No complex lifecycle, no ML, no workers (except nightly cleanup).
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Post(Base):
    """
    Post/Video model (simplified "seed").
    
    - 24 hour lifespan (no extensions)
    - Basic engagement metrics
    - Public or friends-only privacy
    """
    __tablename__ = "posts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Content
    caption = Column(Text, nullable=True)
    video_url = Column(String(512), nullable=True)
    thumbnail_url = Column(String(512), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Engagement counts (denormalized for performance)
    view_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    share_count = Column(Integer, nullable=False, default=0)
    
    # Privacy (MVP: public or friends only)
    is_public = Column(Boolean, nullable=False, default=True)
    
    # Expiration (24 hours fixed)
    expires_at = Column(DateTime, nullable=False)
    soft_deleted = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id])
    comments = relationship("MvpComment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    
    @property
    def is_expired(self) -> bool:
        """Check if post has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def hours_remaining(self) -> float:
        """Hours until expiration."""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.utcnow()
        return delta.total_seconds() / 3600


class MvpComment(Base):
    """
    MVP Comment model (simplified "soil").
    
    - 7 day lifespan (no extensions for MVP)
    - Upvote/downvote counts
    """
    __tablename__ = "mvp_comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    content = Column(Text, nullable=False)
    
    # Votes (denormalized)
    upvote_count = Column(Integer, nullable=False, default=0)
    downvote_count = Column(Integer, nullable=False, default=0)
    
    # Expiration (7 days fixed for MVP)
    expires_at = Column(DateTime, nullable=False)
    soft_deleted = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])
    votes = relationship("CommentVote", back_populates="comment", cascade="all, delete-orphan")
    
    @property
    def net_votes(self) -> int:
        """Net vote score (upvotes - downvotes)."""
        return self.upvote_count - self.downvote_count


class Like(Base):
    """
    Like model (symbolic "watering").
    
    Simple like/unlike functionality.
    """
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='uq_post_user_like'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    post = relationship("Post", back_populates="likes")
    user = relationship("User")


class CommentVote(Base):
    """
    Comment vote model (upvote/downvote).
    
    Tracks individual votes on comments.
    """
    __tablename__ = "comment_votes"
    __table_args__ = (
        UniqueConstraint('comment_id', 'user_id', name='uq_comment_user_vote'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment_id = Column(UUID(as_uuid=True), ForeignKey("mvp_comments.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    vote_type = Column(String(10), nullable=False)  # 'up' or 'down'
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    comment = relationship("MvpComment", back_populates="votes")
    user = relationship("User")


class Follow(Base):
    """
    Follow relationship between users.
    
    Simple follower/following system.
    """
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='uq_follower_following'),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    follower_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    following_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id])
    following = relationship("User", foreign_keys=[following_id])
