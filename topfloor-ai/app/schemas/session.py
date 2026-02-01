"""
Session Schemas - Pydantic models for session validation and serialization
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
import re

from app.models.session import SessionStatus


class SessionBase(BaseModel):
    """Base session schema with common fields"""
    agent_type: str = Field(..., description="Type of agent for this session", min_length=1, max_length=50)
    agent_name: str = Field(..., description="Name of the agent", min_length=1, max_length=100)
    title: Optional[str] = Field(None, description="Optional user-friendly title", max_length=255)
    description: Optional[str] = Field(None, description="Optional description", max_length=2000)
    
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
    
    @field_validator('agent_name')
    @classmethod
    def validate_agent_name(cls, v: str) -> str:
        """Validate agent name format"""
        v = v.strip()
        if not v:
            raise ValueError("Agent name cannot be empty")
        
        # Allow letters, numbers, spaces, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9 _\-]+$', v):
            raise ValueError("Agent name contains invalid characters")
        
        return v
    
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
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Input contains potentially dangerous content")
        
        return v.strip()


class SessionCreate(SessionBase):
    """Schema for creating a new session"""
    pass


class SessionUpdate(BaseModel):
    """Schema for updating a session"""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[SessionStatus] = None
    
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
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Input contains potentially dangerous content")
        
        return v.strip()


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
