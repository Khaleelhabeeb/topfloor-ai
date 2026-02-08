"""
Memory API endpoints for long-term memory management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel, Field

from app.services.memory_service import get_memory_service, Memory
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter(prefix="/memory", tags=["memory"])


# Pydantic schemas
class MemoryCreate(BaseModel):
    """Schema for creating a new memory."""
    agent_type: str = Field(..., description="Agent type (finance, data_analyst, researcher, team_lead)")
    content: str = Field(..., min_length=1, max_length=5000, description="Memory content")
    importance: float = Field(0.5, ge=0.0, le=1.0, description="Importance score (0-1)")
    memory_type: str = Field("fact", description="Memory type (preference, fact, decision, summary)")
    tags: Optional[List[str]] = Field(None, description="Optional tags for categorization")


class MemoryResponse(BaseModel):
    """Schema for memory response."""
    id: str
    content: str
    user_id: int
    agent_type: str
    importance: float
    memory_type: str
    tags: List[str]
    created_at: str
    last_accessed: str
    access_count: int
    metadata: Optional[dict] = None


class MemorySearchRequest(BaseModel):
    """Schema for memory search."""
    query: str = Field(..., min_length=1, description="Search query")
    agent_type: Optional[str] = Field(None, description="Filter by agent type")
    limit: int = Field(5, ge=1, le=20, description="Maximum results")
    min_importance: float = Field(0.0, ge=0.0, le=1.0, description="Minimum importance")


class MemoryStats(BaseModel):
    """Schema for memory statistics."""
    total_memories: int
    by_agent: dict
    by_type: dict
    avg_importance: float


@router.post("", response_model=dict, status_code=201)
async def create_memory(
    memory_data: MemoryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new memory for the current user.
    
    Args:
        memory_data: Memory creation data
        current_user: Authenticated user
        
    Returns:
        Created memory ID
    """
    memory_service = get_memory_service()
    
    memory_id = memory_service.store(
        user_id=current_user.id,
        agent_type=memory_data.agent_type,
        content=memory_data.content,
        importance=memory_data.importance,
        memory_type=memory_data.memory_type,
        tags=memory_data.tags or []
    )
    
    return {"memory_id": memory_id, "message": "Memory created successfully"}


@router.get("/search", response_model=List[MemoryResponse])
async def search_memories(
    query: str = Query(..., min_length=1, description="Search query"),
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    limit: int = Query(5, ge=1, le=20, description="Maximum results"),
    min_importance: float = Query(0.0, ge=0.0, le=1.0, description="Minimum importance"),
    current_user: User = Depends(get_current_user)
):
    """
    Search for relevant memories using semantic similarity.
    
    Args:
        query: Search query text
        agent_type: Optional agent type filter
        limit: Maximum number of results
        min_importance: Minimum importance score
        current_user: Authenticated user
        
    Returns:
        List of relevant memories
    """
    memory_service = get_memory_service()
    
    memories = memory_service.search(
        query=query,
        user_id=current_user.id,
        agent_type=agent_type,
        limit=limit,
        min_importance=min_importance
    )
    
    return [MemoryResponse(**memory.to_dict()) for memory in memories]


@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    memory_type: Optional[str] = Query(None, description="Filter by memory type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    current_user: User = Depends(get_current_user)
):
    """
    List memories for the current user with optional filters.
    
    Args:
        agent_type: Optional agent type filter
        memory_type: Optional memory type filter
        limit: Maximum number of results
        current_user: Authenticated user
        
    Returns:
        List of memories
    """
    memory_service = get_memory_service()
    
    memories = memory_service.list_memories(
        user_id=current_user.id,
        agent_type=agent_type,
        memory_type=memory_type,
        limit=limit
    )
    
    return [MemoryResponse(**memory.to_dict()) for memory in memories]


@router.get("/stats", response_model=MemoryStats)
async def get_memory_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get memory statistics for the current user.
    
    Args:
        current_user: Authenticated user
        
    Returns:
        Memory statistics
    """
    memory_service = get_memory_service()
    stats = memory_service.get_stats(current_user.id)
    return MemoryStats(**stats)


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific memory by ID.
    
    Args:
        memory_id: Memory ID
        current_user: Authenticated user
        
    Returns:
        Memory object
    """
    memory_service = get_memory_service()
    memory = memory_service.retrieve(memory_id)
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # Check ownership
    if memory.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this memory")
    
    return MemoryResponse(**memory.to_dict())


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific memory.
    
    Args:
        memory_id: Memory ID
        current_user: Authenticated user
    """
    memory_service = get_memory_service()
    
    # Check ownership before deleting
    memory = memory_service.retrieve(memory_id)
    if memory and memory.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this memory")
    
    success = memory_service.delete(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")


@router.delete("", status_code=200)
async def delete_all_memories(
    agent_type: Optional[str] = Query(None, description="Filter by agent type"),
    current_user: User = Depends(get_current_user)
):
    """
    Delete all memories for the current user (optionally filtered by agent type).
    
    Args:
        agent_type: Optional agent type filter
        current_user: Authenticated user
        
    Returns:
        Number of memories deleted
    """
    memory_service = get_memory_service()
    
    count = memory_service.delete_user_memories(
        user_id=current_user.id,
        agent_type=agent_type
    )
    
    return {"deleted_count": count, "message": f"Deleted {count} memories"}


@router.post("/prune", status_code=200)
async def prune_memories(
    days_old: int = Query(30, ge=1, description="Delete memories older than this many days"),
    min_importance: float = Query(0.3, ge=0.0, le=1.0, description="Minimum importance threshold"),
    max_access_count: int = Query(2, ge=0, description="Maximum access count threshold"),
    current_user: User = Depends(get_current_user)
):
    """
    Prune old, low-importance, rarely accessed memories.
    
    Args:
        days_old: Delete memories older than this many days
        min_importance: Delete memories with importance below this
        max_access_count: Delete memories accessed fewer times than this
        current_user: Authenticated user
        
    Returns:
        Number of memories pruned
    """
    memory_service = get_memory_service()
    
    count = memory_service.prune_old_memories(
        user_id=current_user.id,
        days_old=days_old,
        min_importance=min_importance,
        max_access_count=max_access_count
    )
    
    return {"pruned_count": count, "message": f"Pruned {count} memories"}
