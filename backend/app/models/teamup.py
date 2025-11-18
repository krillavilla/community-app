"""
Team Up feature models.

Collaborative projects with members, roles, and discussions.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ProjectType(str, enum.Enum):
    """Type of TeamUp project."""
    LEARNING = "learning"
    CREATIVE = "creative"
    SERVICE = "service"
    ACCOUNTABILITY = "accountability"
    RESEARCH = "research"
    OTHER = "other"


class ProjectStatus(str, enum.Enum):
    """Project lifecycle status."""
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectRole(str, enum.Enum):
    """Member role within a project."""
    CREATOR = "creator"
    CO_LEAD = "co_lead"
    MEMBER = "member"
    GUEST = "guest"


class ProjectVisibility(str, enum.Enum):
    """Project visibility settings."""
    PUBLIC = "public"
    GOOD_SOIL_PLUS = "good_soil_plus"
    PRIVATE = "private"


class Project(Base):
    """
    TeamUp collaborative project.
    
    Community-driven projects with multiple members.
    """
    __tablename__ = "projects"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to User (creator)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Project details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    project_type = Column(SQLEnum(ProjectType), nullable=False)
    
    # Goals and progress
    goals = Column(Text, nullable=True)  # JSON array serialized as text
    progress_percentage = Column(Integer, default=0, nullable=False)
    
    # Status
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.PLANNING)
    visibility = Column(SQLEnum(ProjectVisibility), nullable=False, default=ProjectVisibility.PUBLIC)
    
    # Settings
    max_members = Column(Integer, default=10, nullable=False)
    is_accepting_members = Column(Boolean, default=True, nullable=False)
    
    # Spiritual content
    is_spiritual = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", backref="projects_created")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    discussions = relationship("ProjectDiscussion", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project '{self.title}' ({self.status})>"


class ProjectMember(Base):
    """
    Membership in a TeamUp project.
    
    Tracks member role and contribution metrics.
    """
    __tablename__ = "project_members"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Role
    role = Column(SQLEnum(ProjectRole), nullable=False, default=ProjectRole.MEMBER)
    
    # Optional bio for this project
    member_bio = Column(Text, nullable=True)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="members")
    user = relationship("User", backref="project_memberships")
    
    def __repr__(self):
        return f"<ProjectMember User {self.user_id} in Project {self.project_id} as {self.role}>"


class ProjectDiscussion(Base):
    """
    Discussion post within a project.
    
    Thread-based communication for project coordination.
    """
    __tablename__ = "project_discussions"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    parent_discussion_id = Column(UUID(as_uuid=True), ForeignKey("project_discussions.id"), nullable=True)
    
    # Content
    content = Column(Text, nullable=False)
    
    # Optional attachment
    attachment_url = Column(String(500), nullable=True)
    
    # Moderation
    is_pinned = Column(Boolean, default=False, nullable=False)
    is_flagged = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="discussions")
    author = relationship("User", backref="project_discussions")
    parent_discussion = relationship("ProjectDiscussion", remote_side=[id], backref="replies")
    
    def __repr__(self):
        return f"<ProjectDiscussion {self.id} in Project {self.project_id}>"
