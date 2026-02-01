"""
Task Schemas - Pydantic models for task management
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import re


class TaskType(str, Enum):
    """Task type enumeration"""
    CHAT = "chat"
    BACKGROUND = "background"


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
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
    description: Optional[str] = Field(None, description="Task description", max_length=5000)
    agent_type: str = Field(..., description="Agent type to handle this task", min_length=1, max_length=50)
    task_type: TaskType = Field(TaskType.BACKGROUND, description="Task type (chat or background)")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    input_data: Optional[Dict[str, Any]] = Field(None, description="Input data for the task")
    
    @field_validator('title', 'description')
    @classmethod
    def validate_no_xss(cls, v: Optional[str]) -> Optional[str]:
        """Prevent XSS attacks by checking for script tags and dangerous patterns"""
        if v is None:
            return v
        
        # Check for common XSS patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',  # onclick, onload, etc.
            r'<iframe',
            r'<object',
            r'<embed',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Input contains potentially dangerous content")
        
        return v.strip()
    
    @field_validator('agent_type')
    @classmethod
    def validate_agent_type(cls, v: str) -> str:
        """Validate agent type format"""
        if not re.match(r'^[a-z_]+$', v):
            raise ValueError("Agent type must contain only lowercase letters and underscores")
        
        # Validate against known agent types
        valid_agents = ['orchestrator', 'team_lead', 'finance', 'data_analyst', 'researcher']
        if v not in valid_agents:
            raise ValueError(f"Invalid agent type. Must be one of: {', '.join(valid_agents)}")
        
        return v
    
    @field_validator('input_data')
    @classmethod
    def validate_input_data_size(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate input data is not too large"""
        if v is not None:
            # Convert to string to check size (rough estimate)
            import json
            data_str = json.dumps(v)
            if len(data_str) > 100000:  # 100KB limit
                raise ValueError("Input data exceeds maximum size of 100KB")
        return v


class TaskUpdate(BaseModel):
    """Request to update a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated task title")
    description: Optional[str] = Field(None, max_length=5000, description="Updated task description")
    status: Optional[TaskStatus] = Field(None, description="Updated task status")
    priority: Optional[TaskPriority] = Field(None, description="Updated task priority")
    result_data: Optional[Dict[str, Any]] = Field(None, description="Task result data")
    error_message: Optional[str] = Field(None, max_length=2000, description="Error message if task failed")
    
    @field_validator('title', 'description', 'error_message')
    @classmethod
    def validate_no_xss(cls, v: Optional[str]) -> Optional[str]:
        """Prevent XSS attacks by checking for script tags and dangerous patterns"""
        if v is None:
            return v
        
        # Check for common XSS patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Input contains potentially dangerous content")
        
        return v.strip()
    
    @field_validator('result_data')
    @classmethod
    def validate_result_data_size(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate result data is not too large"""
        if v is not None:
            import json
            data_str = json.dumps(v)
            if len(data_str) > 500000:  # 500KB limit for results
                raise ValueError("Result data exceeds maximum size of 500KB")
        return v
    
    @model_validator(mode='after')
    def validate_at_least_one_field(self):
        """Ensure at least one field is being updated"""
        if all(getattr(self, field) is None for field in ['title', 'description', 'status', 'priority', 'result_data', 'error_message']):
            raise ValueError("At least one field must be provided for update")
        return self


class TaskResponse(BaseModel):
    """Response for a task"""
    id: int
    task_id: str
    user_id: int
    title: str
    description: Optional[str]
    agent_type: str
    task_type: TaskType
    status: TaskStatus
    priority: TaskPriority
    input_data: Optional[Dict[str, Any]]
    result_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Response for listing tasks"""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int
