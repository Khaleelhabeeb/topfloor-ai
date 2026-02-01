"""
Agent Schemas - Pydantic models for agent status and management
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re


class AgentStatusEnum(str, Enum):
    """Agent status enumeration"""
    AVAILABLE = "available"
    BUSY = "busy"
    IDLE = "idle"


class AgentStatusResponse(BaseModel):
    """Response for agent status"""
    id: int
    user_id: int
    agent_type: str
    status: AgentStatusEnum
    current_task_id: Optional[int]
    tasks_in_queue: int
    last_active_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
