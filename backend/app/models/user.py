"""
User and Guide-related data models.

Includes User, GuideProfile, GuideApplication, and TrustVerificationApplication.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    USER = "user"
    GUIDE = "guide"
    GUARDIAN = "guardian"


class TrustLevel(str, enum.Enum):
    """Trust level progression for community members."""
    NEW_SPROUT = "new_sprout"  # Default for new users
    GROWING = "growing"  # Active participation
    GOOD_SOIL = "good_soil"  # Consistent positive contributions
    FLOURISHING = "flourishing"  # Exemplary community member


class ApplicationStatus(str, enum.Enum):
    """Status for Guide and Trust Verification applications."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    """
    Core user model.
    
    Represents a Garden Platform member with Auth0 authentication,
    trust level, and role-based permissions.
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Auth0 authentication
    auth0_sub = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # Profile
    display_name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Role and Trust
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    trust_level = Column(SQLEnum(TrustLevel), nullable=False, default=TrustLevel.NEW_SPROUT)
    
    # Guide status
    is_verified_guide = Column(Boolean, default=False, nullable=False)
    
    # Content preferences
    spiritual_opt_in = Column(Boolean, default=False, nullable=False)
    
    # Metrics (TODO: compute from relationships in production)
    streak_days = Column(Integer, default=0, nullable=False)
    total_habits_completed = Column(Integer, default=0, nullable=False)
    connection_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_active_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    guide_profile = relationship("GuideProfile", back_populates="user", uselist=False)
    guide_applications = relationship("GuideApplication", back_populates="user")
    trust_applications = relationship("TrustVerificationApplication", back_populates="user")
    
    # TODO: Add relationships to other models (habits, posts, etc.) as they are created
    
    def __repr__(self):
        return f"<User {self.display_name} ({self.email})>"


class GuideProfile(Base):
    """
    Extended profile for verified Guides.
    
    Created when a user's Guide application is approved.
    """
    __tablename__ = "guide_profiles"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Guide details
    expertise_areas = Column(Text, nullable=True)  # JSON array serialized as text
    years_experience = Column(Integer, nullable=True)
    availability_hours = Column(Text, nullable=True)  # JSON object serialized as text
    mentorship_capacity = Column(Integer, default=5, nullable=False)
    current_mentees = Column(Integer, default=0, nullable=False)
    
    # Verification
    verified_at = Column(DateTime, nullable=False)
    verified_by_guardian_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Metrics
    total_mentees = Column(Integer, default=0, nullable=False)
    avg_rating = Column(Integer, default=0, nullable=False)  # Out of 5, stored as int * 100
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="guide_profile", foreign_keys=[user_id])
    verified_by_guardian = relationship("User", foreign_keys=[verified_by_guardian_id])
    
    def __repr__(self):
        return f"<GuideProfile for User {self.user_id}>"


class GuideApplication(Base):
    """
    Application to become a verified Guide.
    
    Requires Good Soil trust level and Guardian approval.
    """
    __tablename__ = "guide_applications"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Application content
    motivation = Column(Text, nullable=False)
    expertise_areas = Column(Text, nullable=False)
    relevant_experience = Column(Text, nullable=False)
    
    # Status
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    
    # Review
    reviewed_by_guardian_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="guide_applications", foreign_keys=[user_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_guardian_id])
    
    def __repr__(self):
        return f"<GuideApplication {self.id} by User {self.user_id} - {self.status}>"


class TrustVerificationApplication(Base):
    """
    Application for trust level promotion to Good Soil.
    
    Users can apply once they meet contribution thresholds.
    Reviewed by Guardians.
    """
    __tablename__ = "trust_verification_applications"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Application content
    contributions_summary = Column(Text, nullable=False)
    why_good_soil = Column(Text, nullable=False)
    
    # Requested level
    requested_level = Column(SQLEnum(TrustLevel), nullable=False)
    
    # Status
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING, nullable=False)
    
    # Review
    reviewed_by_guardian_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="trust_applications", foreign_keys=[user_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_guardian_id])
    
    def __repr__(self):
        return f"<TrustVerificationApplication {self.id} by User {self.user_id} - {self.status}>"
