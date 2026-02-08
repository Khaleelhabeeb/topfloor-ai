"""
Agent Schemas - Pydantic models for agent status and management
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
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


class AgentInfo(BaseModel):
    """Information about an agent"""
    name: str
    agent_type: str
    description: str


class AgentListResponse(BaseModel):
    """Response for listing agents"""
    agents: List[AgentInfo]
    total: int


class AgentExecutionRequest(BaseModel):
    """Request to execute an agent"""
    message: str = Field(..., description="User message to send to the agent", min_length=1)
    agent_type: Optional[str] = Field(None, description="Specific agent type to use (defaults to orchestrator)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the agent")


class AgentExecutionResponse(BaseModel):
    """Response from agent execution"""
    session_id: str
    agent_name: str
    response: str
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
