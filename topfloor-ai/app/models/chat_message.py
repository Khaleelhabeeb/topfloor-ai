"""
ChatMessage Model - Stores conversation messages between users and agents
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class MessageRole(str, enum.Enum):
    """Message role enumeration"""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class ChatMessage(Base):
    """
    ChatMessage model for storing conversation messages.
    
    Each message represents a single message in a conversation between
    a user and an agent. Messages are:
    - Persistent: Stored in database for history
    - Ordered: Timestamped for chronological retrieval
    - Scoped: Associated with user, agent, and session
    - Flexible: Support metadata for extensions
    
    Messages support:
    - Full conversation history
    - Multi-agent conversations
    - Session-based grouping
    - Metadata for rich content
    """
    
    __tablename__ = "chat_messages"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Message identification
    message_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Session association
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Agent information
    agent_type = Column(String(50), nullable=False, index=True)
    
    # Message details
    role = Column(
        SQLEnum(MessageRole, name="message_role"),
        nullable=False
    )
    
    content = Column(Text, nullable=False)
    
    # Metadata for extensions (e.g., attachments, formatting, tool calls)
    # Note: Using 'message_metadata' instead of 'metadata' as 'metadata' is reserved by SQLAlchemy
    message_metadata = Column(JSONB, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, index=True)
    
    # Relationships
    session = relationship("Session", backref="messages")
    user = relationship("User", backref="messages")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('idx_user_agent_created', 'user_id', 'agent_type', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, message_id={self.message_id}, user_id={self.user_id}, agent_type={self.agent_type}, role={self.role})>"
    
    def to_dict(self) -> dict:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "message_id": self.message_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "agent_type": self.agent_type,
            "role": self.role.value,
            "content": self.content,
            "metadata": self.message_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
