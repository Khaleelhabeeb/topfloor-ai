"""
TaskHistory Model - Tracks status changes and events for tasks
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Index, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


# Use JSON type with JSONB for PostgreSQL (falls back to JSON for SQLite)
JSONType = JSON().with_variant(JSONB(), 'postgresql')


class TaskHistory(Base):
    """
    TaskHistory model for tracking task status changes and events.
    
    This model maintains an audit trail of all status changes and important
    events that occur during a task's lifecycle. Each record represents a
    single event or status change.
    
    Use cases:
    - Track when a task moves from pending to queued to in_progress
    - Log important events during task execution
    - Store metadata about status changes
    - Provide audit trail for debugging and monitoring
    """
    
    __tablename__ = "task_history"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Task association
    task_id = Column(
        Integer, 
        ForeignKey("tasks.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Status information
    status = Column(String(20), nullable=False)
    
    # Event details
    message = Column(Text, nullable=True)
    
    # Additional metadata (using 'event_metadata' to avoid SQLAlchemy reserved name)
    event_metadata = Column("metadata", JSONType, nullable=True)
    
    # Timestamp
    created_at = Column(
        DateTime(timezone=True), 
        nullable=False, 
        default=datetime.utcnow
    )
    
    # Relationships
    task = relationship("Task", backref="history")
    
    # Composite indexes for common query patterns
    __table_args__ = (
        # Index for querying history by task and timestamp (audit trail)
        Index('idx_task_history_task_created', 'task_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<TaskHistory(id={self.id}, task_id={self.task_id}, status={self.status}, created_at={self.created_at})>"
    
    def to_dict(self) -> dict:
        """Convert task history to dictionary"""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "status": self.status,
            "message": self.message,
            "metadata": self.event_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
