"""
The Orchard feature models.

Connections, messaging, and mentorship relationships.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class ConnectionType(str, enum.Enum):
    """Type of connection between users."""
    FRIEND = "friend"
    MENTOR = "mentor"
    MENTEE = "mentee"
    ACCOUNTABILITY_PARTNER = "accountability_partner"


class ConnectionStatus(str, enum.Enum):
    """Status of connection request."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class MentorshipStatus(str, enum.Enum):
    """Status of mentorship relationship."""
    REQUESTED = "requested"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Connection(Base):
    """
    Connection between two users.
    
    Symmetric relationship once accepted (both users are connected).
    """
    __tablename__ = "connections"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys to Users
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    addressee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Connection details
    connection_type = Column(SQLEnum(ConnectionType), nullable=False, default=ConnectionType.FRIEND)
    status = Column(SQLEnum(ConnectionStatus), nullable=False, default=ConnectionStatus.PENDING)
    
    # Optional message with request
    request_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], backref="connections_sent")
    addressee = relationship("User", foreign_keys=[addressee_id], backref="connections_received")
    
    def __repr__(self):
        return f"<Connection {self.requester_id} -> {self.addressee_id} ({self.status})>"


class Message(Base):
    """
    Private message between connected users.
    
    Requires active Connection between sender and receiver.
    """
    __tablename__ = "messages"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys to Users
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Content
    content = Column(Text, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # Moderation
    is_flagged = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], backref="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], backref="messages_received")
    
    def __repr__(self):
        return f"<Message {self.id} from {self.sender_id} to {self.receiver_id}>"


class MentorshipRequest(Base):
    """
    Formal mentorship request from mentee to guide.
    
    Requires guide to have verified Guide status.
    """
    __tablename__ = "mentorship_requests"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys to Users
    mentee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    guide_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Request details
    message = Column(Text, nullable=False)
    areas_of_focus = Column(Text, nullable=True)  # JSON array serialized as text
    
    # Status
    status = Column(SQLEnum(MentorshipStatus), nullable=False, default=MentorshipStatus.REQUESTED)
    
    # Duration (optional)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    mentee = relationship("User", foreign_keys=[mentee_id], backref="mentorship_requests_as_mentee")
    guide = relationship("User", foreign_keys=[guide_id], backref="mentorship_requests_as_guide")
    
    def __repr__(self):
        return f"<MentorshipRequest {self.id} from {self.mentee_id} to {self.guide_id} ({self.status})>"
