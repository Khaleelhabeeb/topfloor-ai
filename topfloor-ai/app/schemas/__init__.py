"""
Pydantic schemas for API request/response validation
"""

from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.schemas.task import (
    TaskType,
    TaskStatus,
    TaskPriority,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from app.schemas.chat_message import (
    MessageRole,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatMessageListResponse,
)
from app.schemas.artifact import (
    ArtifactCreate,
    ArtifactResponse,
    ArtifactListResponse,
)
from app.schemas.agent import (
    AgentStatusEnum,
    AgentStatusResponse,
)

__all__ = [
    # User schemas
    "UserCreate",
    "UserResponse",
    "UserLogin",
    "Token",
    # Task schemas
    "TaskType",
    "TaskStatus",
    "TaskPriority",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    # Chat message schemas
    "MessageRole",
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ChatMessageListResponse",
    # Artifact schemas
    "ArtifactCreate",
    "ArtifactResponse",
    "ArtifactListResponse",
    # Agent schemas
    "AgentStatusEnum",
    "AgentStatusResponse",
]
