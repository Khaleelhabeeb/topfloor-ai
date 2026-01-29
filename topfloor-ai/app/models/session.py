"""
Session Model - Tracks agent conversations and their lifecycle
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class SessionStatus(str, enum.Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    FAILED = "failed"


class Session(Base):
    """
    Session model for tracking agent conversations.
    
    Each session represents a conversation between a user and an agent.
    Sessions are:
    - Persistent: Stored in database
    - Resumable: Can be continued later
    - Isolated: Scoped per user and agent
    - Traceable: Full lifecycle tracking
    """
    
    __tablename__ = "sessions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Session identification
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Agent information
    agent_type = Column(String(50), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False)
    
    # Session status
    status = Column(
        SQLEnum(SessionStatus, name="session_status"),
        nullable=False,
        default=SessionStatus.ACTIVE,
        index=True
    )
    
    # Session metadata
    title = Column(String(255), nullable=True)  # Optional user-friendly title
    description = Column(Text, nullable=True)  # Optional description
    
    # Lifecycle timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    archived_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, session_id={self.session_id}, user_id={self.user_id}, agent_type={self.agent_type}, status={self.status})>"
    
    def to_dict(self) -> dict:
        """Convert session to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_type": self.agent_type,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "archived_at": self.archived_at.isoformat() if self.archived_at else None,
        }
