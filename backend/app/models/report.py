"""
Content reporting and moderation models.

Used by Guardians for community moderation.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ReportReason(str, enum.Enum):
    """Reason for content report."""
    HARASSMENT = "harassment"
    HATE_SPEECH = "hate_speech"
    SPAM = "spam"
    MISINFORMATION = "misinformation"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    SELF_HARM = "self_harm"
    VIOLENCE = "violence"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    """Status of report review."""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class ReportContentType(str, enum.Enum):
    """Type of content being reported."""
    FLOURISH_POST = "flourish_post"
    COMMENT = "comment"
    SUNLIGHT_POST = "sunlight_post"
    MESSAGE = "message"
    SUPPORT_REQUEST = "support_request"
    SUPPORT_RESPONSE = "support_response"
    PROJECT = "project"
    PROJECT_DISCUSSION = "project_discussion"


class Report(Base):
    """
    Content moderation report.
    
    Submitted by community members, reviewed by Guardians.
    """
    __tablename__ = "reports"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Reporter (can be None for anonymous reports)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Content being reported
    content_type = Column(SQLEnum(ReportContentType), nullable=False)
    content_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Report details
    reason = Column(SQLEnum(ReportReason), nullable=False)
    description = Column(Text, nullable=True)
    
    # Review
    status = Column(SQLEnum(ReportStatus), nullable=False, default=ReportStatus.PENDING)
    reviewed_by_guardian_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Action taken
    action_taken = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], backref="reports_submitted")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_guardian_id], backref="reports_reviewed")
    
    def __repr__(self):
        return f"<Report {self.id} for {self.content_type} ({self.status})>"
