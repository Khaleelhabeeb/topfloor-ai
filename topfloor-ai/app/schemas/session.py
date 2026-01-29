"""
Session Schemas - Pydantic models for session validation and serialization
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from app.models.session import SessionStatus


class SessionBase(BaseModel):
    """Base session schema with common fields"""
    agent_type: str = Field(..., description="Type of agent for this session")
    agent_name: str = Field(..., description="Name of the agent")
    title: Optional[str] = Field(None, description="Optional user-friendly title")
    description: Optional[str] = Field(None, description="Optional description")


class SessionCreate(SessionBase):
    """Schema for creating a new session"""
    pass


class SessionUpdate(BaseModel):
    """Schema for updating a session"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[SessionStatus] = None


class SessionResponse(SessionBase):
    """Schema for session responses"""
    id: int
    session_id: str
    user_id: int
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class SessionListResponse(BaseModel):
    """Schema for paginated session list"""
    sessions: list[SessionResponse]
    total: int
    page: int
    page_size: int
    
    model_config = ConfigDict(from_attributes=True)
