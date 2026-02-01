"""
ChatMessage Schemas - Pydantic models for chat message management
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import re


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class ChatMessageCreate(BaseModel):
    """Request to create a new chat message"""
    session_id: int = Field(..., description="Session ID this message belongs to", gt=0)
    agent_type: str = Field(..., description="Agent type for this conversation", min_length=1, max_length=50)
    role: MessageRole = Field(..., description="Message role (user, agent, or system)")
    content: str = Field(..., description="Message content", min_length=1, max_length=50000)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the message")
    
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
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate message content"""
        # Strip whitespace
        v = v.strip()
        
        # Ensure not empty after stripping
        if not v:
            raise ValueError("Message content cannot be empty")
        
        # Check for excessively long messages
        if len(v) > 50000:
            raise ValueError("Message content exceeds maximum length of 50,000 characters")
        
        return v
    
    @field_validator('metadata')
    @classmethod
    def validate_metadata_size(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate metadata is not too large"""
        if v is not None:
            import json
            data_str = json.dumps(v)
            if len(data_str) > 10000:  # 10KB limit for metadata
                raise ValueError("Metadata exceeds maximum size of 10KB")
        return v


class ChatMessageResponse(BaseModel):
    """Response for a chat message"""
    id: int
    message_id: str
    session_id: int
    user_id: int
    agent_type: str
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = Field(None, alias="message_metadata")
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ChatMessageListResponse(BaseModel):
    """Response for listing chat messages"""
    messages: List[ChatMessageResponse]
    total: int
    page: int
    page_size: int
