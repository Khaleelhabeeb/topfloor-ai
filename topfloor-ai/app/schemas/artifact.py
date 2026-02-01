"""
Artifact Schemas - Pydantic models for artifact management
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import re


class ArtifactCreate(BaseModel):
    """Request to create a new artifact"""
    task_id: Optional[int] = Field(None, description="Associated task ID (optional)", gt=0)
    agent_type: str = Field(..., description="Agent type that generated this artifact", min_length=1, max_length=50)
    file_name: str = Field(..., description="File name", min_length=1, max_length=255)
    file_type: str = Field(..., description="File type (pdf, docx, png, svg, csv, etc)", min_length=1, max_length=50)
    file_path: str = Field(..., description="Storage path (local or cloud)", min_length=1, max_length=500)
    file_size: int = Field(..., description="File size in bytes", gt=0, le=100_000_000)  # Max 100MB
    mime_type: Optional[str] = Field(None, description="MIME type for proper serving", max_length=100)
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata (dimensions, pages, etc)")
    
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
    
    @field_validator('file_name')
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        """Validate file name is safe"""
        # Remove any path traversal attempts
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError("File name cannot contain path traversal characters")
        
        # Check for valid file name characters
        if not re.match(r'^[a-zA-Z0-9_\-. ]+$', v):
            raise ValueError("File name contains invalid characters")
        
        return v.strip()
    
    @field_validator('file_type')
    @classmethod
    def validate_file_type(cls, v: str) -> str:
        """Validate file type is allowed"""
        allowed_types = [
            'pdf', 'docx', 'doc', 'xlsx', 'xls', 'csv',
            'png', 'jpg', 'jpeg', 'svg', 'gif',
            'txt', 'json', 'html', 'xml'
        ]
        
        v_lower = v.lower().strip()
        if v_lower not in allowed_types:
            raise ValueError(f"File type '{v}' is not allowed. Allowed types: {', '.join(allowed_types)}")
        
        return v_lower
    
    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path is safe"""
        # Basic path validation - prevent path traversal
        if '..' in v:
            raise ValueError("File path cannot contain '..' for security reasons")
        
        return v.strip()
    
    @field_validator('mime_type')
    @classmethod
    def validate_mime_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate MIME type format"""
        if v is None:
            return v
        
        # Basic MIME type validation (type/subtype)
        if not re.match(r'^[a-z]+/[a-z0-9\-\+\.]+$', v.lower()):
            raise ValueError("Invalid MIME type format")
        
        return v.lower().strip()
    
    @field_validator('metadata')
    @classmethod
    def validate_metadata_size(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate metadata is not too large"""
        if v is not None:
            import json
            data_str = json.dumps(v)
            if len(data_str) > 50000:  # 50KB limit for metadata
                raise ValueError("Metadata exceeds maximum size of 50KB")
        return v


class ArtifactResponse(BaseModel):
    """Response for an artifact"""
    id: int
    artifact_id: str
    task_id: Optional[int]
    user_id: int
    agent_type: str
    file_name: str
    file_type: str
    file_path: str
    file_size: int
    mime_type: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ArtifactListResponse(BaseModel):
    """Response for listing artifacts"""
    artifacts: List[ArtifactResponse]
    total: int
    page: int
    page_size: int
