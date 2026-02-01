"""
AgentStatus Model - Tracks agent state and availability
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class AgentStatusEnum(str, enum.Enum):
    """Agent status enumeration"""
    AVAILABLE = "available"
    BUSY = "busy"
    IDLE = "idle"


class AgentStatus(Base):
    """
    AgentStatus model for tracking agent state and availability.
    
    Each record represents the current state of an agent for a specific user.
    This enables:
    - Real-time status tracking (available, busy, idle)
    - Current task monitoring
    - Queue length visibility
    - Last activity tracking
    
    The model maintains one record per user-agent pair, updated as the agent
    processes tasks and changes state.
    """
    
    __tablename__ = "agent_status"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Agent identification
    agent_type = Column(String(50), nullable=False, index=True)
    
    # Agent status
    status = Column(
        SQLEnum(AgentStatusEnum, name="agent_status_enum"),
        nullable=False,
        default=AgentStatusEnum.AVAILABLE
    )
    
    # Current task tracking
    current_task_id = Column(
        Integer, 
        ForeignKey("tasks.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Queue management
    tasks_in_queue = Column(Integer, nullable=False, default=0)
    
    # Activity tracking
    last_active_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="agent_statuses")
    current_task = relationship("Task", foreign_keys=[current_task_id])
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'agent_type', name='uq_user_agent'),
        # Index for querying agent status by user (all user's agents)
        Index('idx_agent_status_user', 'user_id'),
        # Index for querying by status (finding available agents)
        Index('idx_agent_status_status', 'status'),
    )
    
    def __repr__(self) -> str:
        return f"<AgentStatus(id={self.id}, user_id={self.user_id}, agent_type={self.agent_type}, status={self.status}, tasks_in_queue={self.tasks_in_queue})>"
    
    def to_dict(self) -> dict:
        """Convert agent status to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "agent_type": self.agent_type,
            "status": self.status.value,
            "current_task_id": self.current_task_id,
            "tasks_in_queue": self.tasks_in_queue,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
