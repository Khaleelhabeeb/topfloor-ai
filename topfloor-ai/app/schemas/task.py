"""
Task Schemas - Pydantic models for task management
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskCreate(BaseModel):
    """Request to create a new task"""
    title: str = Field(..., description="Task title", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Task description")
    agent_type: str = Field(..., description="Agent type to handle this task")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional task context")


class TaskUpdate(BaseModel):
    """Request to update a task"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    result: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Response for a task"""
    id: int
    title: str
    description: Optional[str]
    agent_type: str
    status: TaskStatus
    priority: TaskPriority
    session_id: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Response for listing tasks"""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
