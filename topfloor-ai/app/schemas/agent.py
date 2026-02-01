"""
Agent Schemas - Pydantic models for agent API requests/responses
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime


class AgentInfo(BaseModel):
    """Information about an available agent"""
    name: str = Field(..., description="Agent name")
    agent_type: str = Field(..., description="Agent type")
    description: str = Field(..., description="Agent description")
    
    model_config = ConfigDict(from_attributes=True)


class AgentListResponse(BaseModel):
    """Response for listing available agents"""
    agents: List[AgentInfo]
    total: int


class AgentExecutionRequest(BaseModel):
    """Request to execute an agent"""
    message: str = Field(..., description="User message to the agent", min_length=1)
    session_id: Optional[str] = Field(None, description="Optional session ID to resume")
    agent_type: Optional[str] = Field(None, description="Optional specific agent type to use")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional additional context")


class AgentExecutionResponse(BaseModel):
    """Response from agent execution"""
    session_id: str = Field(..., description="Session ID")
    agent_name: str = Field(..., description="Name of agent that responded")
    response: str = Field(..., description="Agent's response")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    created_at: datetime = Field(..., description="Response timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class AgentStreamChunk(BaseModel):
    """Chunk of streamed agent response"""
    type: str = Field(..., description="Chunk type (text, tool_call, transfer, etc.)")
    content: str = Field(..., description="Chunk content")
    agent_name: Optional[str] = Field(None, description="Agent that generated this chunk")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class AgentStatusResponse(BaseModel):
    """Status of an agent execution"""
    session_id: str
    status: str
    agent_name: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None
