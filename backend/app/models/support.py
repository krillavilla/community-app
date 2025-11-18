"""
Anonymous Support Request feature models.

Anonymous posting with bcrypt token hashing for edit authentication.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class SupportCategory(str, enum.Enum):
    """Category of support request."""
    MENTAL_HEALTH = "mental_health"
    ADDICTION = "addiction"
    RELATIONSHIPS = "relationships"
    GRIEF = "grief"
    TRAUMA = "trauma"
    IDENTITY = "identity"
    FAITH_CRISIS = "faith_crisis"
    LIFE_TRANSITION = "life_transition"
    OTHER = "other"


class SupportVisibility(str, enum.Enum):
    """Visibility setting for support requests."""
    PUBLIC = "public"
    GUIDES_ONLY = "guides_only"
    GOOD_SOIL_PLUS = "good_soil_plus"


class SupportStatus(str, enum.Enum):
    """Status of support request."""
    OPEN = "open"
    ACTIVE = "active"  # Has received responses
    RESOLVED = "resolved"
    ARCHIVED = "archived"


class SupportRequest(Base):
    """
    Anonymous support request.
    
    Uses bcrypt token hashing for anonymous edit authentication.
    Token is hashed before storage - only returned once on creation.
    """
    __tablename__ = "support_requests"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Anonymous identifier (no user_id link)
    # TODO: Store only bcrypt hash of editing token
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    
    # Content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(SQLEnum(SupportCategory), nullable=False)
    
    # Visibility and status
    visibility = Column(SQLEnum(SupportVisibility), nullable=False, default=SupportVisibility.PUBLIC)
    status = Column(SQLEnum(SupportStatus), nullable=False, default=SupportStatus.OPEN)
    
    # Spiritual content
    is_spiritual = Column(Boolean, default=False, nullable=False)
    
    # Moderation
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    
    # Engagement metrics (TODO: compute from relationships)
    response_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    responses = relationship("SupportResponse", back_populates="request", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SupportRequest {self.id} '{self.title}' ({self.status})>"


class SupportResponse(Base):
    """
    Response to an anonymous support request.
    
    Can be from verified Guides or other community members.
    """
    __tablename__ = "support_responses"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    request_id = Column(UUID(as_uuid=True), ForeignKey("support_requests.id"), nullable=False)
    responder_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_response_id = Column(UUID(as_uuid=True), ForeignKey("support_responses.id"), nullable=True)
    
    # Content
    content = Column(Text, nullable=False)
    
    # Guide indicator (computed from responder's role)
    is_from_guide = Column(Boolean, default=False, nullable=False)
    
    # Moderation
    is_flagged = Column(Boolean, default=False, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    request = relationship("SupportRequest", back_populates="responses")
    responder = relationship("User", backref="support_responses")
    parent_response = relationship("SupportResponse", remote_side=[id], backref="replies")
    
    def __repr__(self):
        return f"<SupportResponse {self.id} to Request {self.request_id}>"
