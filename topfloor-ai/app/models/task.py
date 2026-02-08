"""
Task Model - Tracks user tasks assigned to agents
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Text, Index, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


# Use JSON type with JSONB for PostgreSQL (falls back to JSON for SQLite)
JSONType = JSON().with_variant(JSONB(), 'postgresql')


class TaskType(str, enum.Enum):
    """Task type enumeration"""
    CHAT = "chat"
    BACKGROUND = "background"


class TaskPriority(str, enum.Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(Base):
    """
    Task model for tracking work assigned to agents.
    
    Each task represents a unit of work that an agent needs to complete.
    Tasks can be:
    - Chat tasks: Immediate, synchronous conversations
    - Background tasks: Queued, asynchronous processing
    
    Tasks support:
    - Priority levels for queue management
    - Status tracking throughout lifecycle
    - Input/output data storage
    - Error tracking
    - Complete audit trail
    """
    
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Task identification
    task_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # User association
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Agent assignment
    agent_type = Column(String(50), nullable=False, index=True)
    
    # Task details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Task classification
    task_type = Column(
        SQLEnum(TaskType, name="task_type"),
        nullable=False,
        default=TaskType.BACKGROUND
    )
    
    priority = Column(
        SQLEnum(TaskPriority, name="task_priority"),
        nullable=False,
        default=TaskPriority.MEDIUM,
        index=True
    )

    # Task progress tracking
    progress = Column(Integer, nullable=False, default=0)
    due_date = Column(DateTime(timezone=True), nullable=True)
    
    # Task status
    status = Column(
        SQLEnum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True
    )
    
    # Task data
    input_data = Column(JSONType, nullable=True)
    result_data = Column(JSONType, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # Lifecycle timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", backref="tasks")
    
    # Composite indexes for common query patterns
    __table_args__ = (
        # Index for querying tasks by user and agent (common for agent office view)
        Index('idx_task_user_agent', 'user_id', 'agent_type'),
        # Index for querying tasks by user, agent, and status (filtering tasks)
        Index('idx_task_user_agent_status', 'user_id', 'agent_type', 'status'),
        # Index for querying tasks by status and priority (queue processing)
        Index('idx_task_status_priority', 'status', 'priority'),
        # Index for querying tasks by agent and status (agent-specific queries)
        Index('idx_task_agent_status', 'agent_type', 'status'),
        # Index for time-based queries (recent tasks, task history)
        Index('idx_task_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, task_id={self.task_id}, user_id={self.user_id}, agent_type={self.agent_type}, status={self.status})>"
    
    def to_dict(self) -> dict:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "agent_type": self.agent_type,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "input_data": self.input_data,
            "result_data": self.result_data,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
