"""
Fellowship Groups feature models.

Interest-based communities with members, events, and RSVPs.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class GroupType(str, enum.Enum):
    """Type of fellowship group."""
    BOOK_CLUB = "book_club"
    STUDY_GROUP = "study_group"
    SUPPORT_CIRCLE = "support_circle"
    HOBBY = "hobby"
    SPIRITUAL_PRACTICE = "spiritual_practice"
    LIFE_STAGE = "life_stage"
    REGIONAL = "regional"
    OTHER = "other"


class GroupVisibility(str, enum.Enum):
    """Group visibility and access settings."""
    PUBLIC = "public"
    GOOD_SOIL_PLUS = "good_soil_plus"
    INVITE_ONLY = "invite_only"


class GroupMemberRole(str, enum.Enum):
    """Member role within group."""
    FACILITATOR = "facilitator"
    CO_FACILITATOR = "co_facilitator"
    MEMBER = "member"


class EventType(str, enum.Enum):
    """Type of group event."""
    MEETING = "meeting"
    WORKSHOP = "workshop"
    SOCIAL = "social"
    SERVICE = "service"
    RETREAT = "retreat"
    OTHER = "other"


class RSVPStatus(str, enum.Enum):
    """RSVP response status."""
    GOING = "going"
    MAYBE = "maybe"
    NOT_GOING = "not_going"


class FellowshipGroup(Base):
    """
    Fellowship group for shared interests.
    
    Community-within-community for focused connection.
    """
    __tablename__ = "fellowship_groups"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to User (creator)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Group details
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    group_type = Column(SQLEnum(GroupType), nullable=False)
    
    # Settings
    visibility = Column(SQLEnum(GroupVisibility), nullable=False, default=GroupVisibility.PUBLIC)
    max_members = Column(Integer, default=50, nullable=False)
    is_accepting_members = Column(Boolean, default=True, nullable=False)
    
    # Spiritual content
    is_spiritual = Column(Boolean, default=False, nullable=False)
    
    # Image
    cover_image_url = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    creator = relationship("User", backref="fellowship_groups_created")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    events = relationship("GroupEvent", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FellowshipGroup '{self.name}' ({self.group_type})>"


class GroupMember(Base):
    """
    Membership in a Fellowship Group.
    
    Tracks role and participation.
    """
    __tablename__ = "group_members"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    group_id = Column(UUID(as_uuid=True), ForeignKey("fellowship_groups.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Role
    role = Column(SQLEnum(GroupMemberRole), nullable=False, default=GroupMemberRole.MEMBER)
    
    # Optional member intro
    intro = Column(Text, nullable=True)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    group = relationship("FellowshipGroup", back_populates="members")
    user = relationship("User", backref="group_memberships")
    
    def __repr__(self):
        return f"<GroupMember User {self.user_id} in Group {self.group_id} as {self.role}>"


class GroupEvent(Base):
    """
    Event organized by a Fellowship Group.
    
    Meetings, workshops, socials, etc. with RSVP tracking.
    """
    __tablename__ = "group_events"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    group_id = Column(UUID(as_uuid=True), ForeignKey("fellowship_groups.id"), nullable=False)
    organizer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Event details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    event_type = Column(SQLEnum(EventType), nullable=False)
    
    # Scheduling
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    
    # Location (optional - can be virtual)
    location = Column(String(300), nullable=True)
    is_virtual = Column(Boolean, default=False, nullable=False)
    virtual_link = Column(String(500), nullable=True)
    
    # RSVP settings
    max_attendees = Column(Integer, nullable=True)  # NULL = unlimited
    rsvp_deadline = Column(DateTime, nullable=True)
    
    # Status
    is_cancelled = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    group = relationship("FellowshipGroup", back_populates="events")
    organizer = relationship("User", backref="group_events_organized")
    rsvps = relationship("EventRSVP", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<GroupEvent '{self.title}' on {self.start_time}>"


class EventRSVP(Base):
    """
    RSVP response to a group event.
    
    One RSVP per user per event.
    """
    __tablename__ = "event_rsvps"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    event_id = Column(UUID(as_uuid=True), ForeignKey("group_events.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # RSVP status
    status = Column(SQLEnum(RSVPStatus), nullable=False)
    
    # Optional note
    note = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship("GroupEvent", back_populates="rsvps")
    user = relationship("User", backref="event_rsvps")
    
    def __repr__(self):
        return f"<EventRSVP User {self.user_id} for Event {self.event_id} ({self.status})>"
