"""
Tests for ChatMessage Schemas
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.chat_message import (
    MessageRole,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatMessageListResponse,
)


class TestChatMessageCreate:
    """Tests for ChatMessageCreate schema."""
    
    def test_valid_chat_message_create_minimal(self):
        """Test that valid minimal chat message creation data is accepted."""
        message = ChatMessageCreate(
            session_id=1,
            agent_type="finance",
            role=MessageRole.USER,
            content="Hello, can you help me?"
        )
        assert message.session_id == 1
        assert message.agent_type == "finance"
        assert message.role == MessageRole.USER
        assert message.content == "Hello, can you help me?"
        assert message.metadata is None
    
    def test_valid_chat_message_create_full(self):
        """Test that valid full chat message creation data is accepted."""
        message = ChatMessageCreate(
            session_id=1,
            agent_type="finance",
            role=MessageRole.AGENT,
            content="I can help you with financial analysis.",
            metadata={"tool_calls": ["fetch_market_data"], "confidence": 0.95}
        )
        assert message.session_id == 1
        assert message.agent_type == "finance"
        assert message.role == MessageRole.AGENT
        assert message.content == "I can help you with financial analysis."
        assert message.metadata == {"tool_calls": ["fetch_market_data"], "confidence": 0.95}
    
    def test_missing_session_id(self):
        """Test that missing session_id is rejected."""
        with pytest.raises(ValidationError):
            ChatMessageCreate(
                agent_type="finance",
                role=MessageRole.USER,
                content="Hello"
            )
    
    def test_missing_agent_type(self):
        """Test that missing agent_type is rejected."""
        with pytest.raises(ValidationError):
            ChatMessageCreate(
                session_id=1,
                role=MessageRole.USER,
                content="Hello"
            )
    
    def test_missing_role(self):
        """Test that missing role is rejected."""
        with pytest.raises(ValidationError):
            ChatMessageCreate(
                session_id=1,
                agent_type="finance",
                content="Hello"
            )
    
    def test_missing_content(self):
        """Test that missing content is rejected."""
        with pytest.raises(ValidationError):
            ChatMessageCreate(
                session_id=1,
                agent_type="finance",
                role=MessageRole.USER
            )
    
    def test_empty_content(self):
        """Test that empty content is rejected."""
        with pytest.raises(ValidationError):
            ChatMessageCreate(
                session_id=1,
                agent_type="finance",
                role=MessageRole.USER,
                content=""
            )
    
    def test_empty_agent_type(self):
        """Test that empty agent_type is rejected."""
        with pytest.raises(ValidationError):
            ChatMessageCreate(
                session_id=1,
                agent_type="",
                role=MessageRole.USER,
                content="Hello"
            )
    
    def test_agent_type_too_long(self):
        """Test that agent_type longer than 50 characters is rejected."""
        with pytest.raises(ValidationError):
            ChatMessageCreate(
                session_id=1,
                agent_type="x" * 51,
                role=MessageRole.USER,
                content="Hello"
            )
    
    def test_agent_type_exactly_50_characters(self):
        """Test that agent_type with exactly 50 characters is rejected (must be valid agent type)."""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessageCreate(
                session_id=1,
                agent_type="x" * 50,
                role=MessageRole.USER,
                content="Hello"
            )
        assert "Invalid agent type" in str(exc_info.value)
    
    def test_all_message_roles(self):
        """Test that all message roles are accepted."""
        for role in MessageRole:
            message = ChatMessageCreate(
                session_id=1,
                agent_type="finance",
                role=role,
                content="Test message"
            )
            assert message.role == role
    
    def test_metadata_dict(self):
        """Test that metadata accepts dictionary."""
        message = ChatMessageCreate(
            session_id=1,
            agent_type="finance",
            role=MessageRole.USER,
            content="Hello",
            metadata={"key": "value", "nested": {"data": 123}}
        )
        assert message.metadata == {"key": "value", "nested": {"data": 123}}
    
    def test_long_content(self):
        """Test that long content is accepted."""
        long_content = "x" * 10000
        message = ChatMessageCreate(
            session_id=1,
            agent_type="finance",
            role=MessageRole.USER,
            content=long_content
        )
        assert message.content == long_content


class TestChatMessageResponse:
    """Tests for ChatMessageResponse schema."""
    
    def test_valid_chat_message_response_minimal(self):
        """Test that valid minimal chat message response is accepted."""
        message = ChatMessageResponse(
            id=1,
            message_id="msg_123",
            session_id=1,
            user_id=1,
            agent_type="finance",
            role=MessageRole.USER,
            content="Hello",
            metadata=None,
            created_at=datetime.now()
        )
        assert message.id == 1
        assert message.message_id == "msg_123"
        assert message.session_id == 1
        assert message.user_id == 1
        assert message.agent_type == "finance"
        assert message.role == MessageRole.USER
        assert message.content == "Hello"
        assert message.metadata is None
    
    def test_valid_chat_message_response_full(self):
        """Test that valid full chat message response is accepted."""
        now = datetime.now()
        message = ChatMessageResponse(
            id=1,
            message_id="msg_123",
            session_id=1,
            user_id=1,
            agent_type="finance",
            role=MessageRole.AGENT,
            content="I can help you with that.",
            metadata={"tool_calls": ["analyze_data"], "tokens": 150},
            created_at=now
        )
        assert message.id == 1
        assert message.message_id == "msg_123"
        assert message.metadata == {"tool_calls": ["analyze_data"], "tokens": 150}
        assert message.created_at == now
    
    def test_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        with pytest.raises(ValidationError):
            ChatMessageResponse(
                id=1,
                message_id="msg_123"
            )
    
    def test_from_attributes_config(self):
        """Test that from_attributes is enabled for SQLAlchemy model conversion."""
        assert ChatMessageResponse.model_config.get('from_attributes') is True
    
    def test_all_roles_in_response(self):
        """Test that all message roles work in response."""
        now = datetime.now()
        for role in MessageRole:
            message = ChatMessageResponse(
                id=1,
                message_id="msg_123",
                session_id=1,
                user_id=1,
                agent_type="finance",
                role=role,
                content="Test",
                metadata=None,
                created_at=now
            )
            assert message.role == role


class TestChatMessageListResponse:
    """Tests for ChatMessageListResponse schema."""
    
    def test_valid_chat_message_list_response(self):
        """Test that valid chat message list response is accepted."""
        now = datetime.now()
        message1 = ChatMessageResponse(
            id=1,
            message_id="msg_1",
            session_id=1,
            user_id=1,
            agent_type="finance",
            role=MessageRole.USER,
            content="Hello",
            metadata=None,
            created_at=now
        )
        
        message_list = ChatMessageListResponse(
            messages=[message1],
            total=1,
            page=1,
            page_size=10
        )
        assert len(message_list.messages) == 1
        assert message_list.total == 1
        assert message_list.page == 1
        assert message_list.page_size == 10
    
    def test_empty_message_list(self):
        """Test that empty message list is accepted."""
        message_list = ChatMessageListResponse(
            messages=[],
            total=0,
            page=1,
            page_size=10
        )
        assert len(message_list.messages) == 0
        assert message_list.total == 0
    
    def test_multiple_messages(self):
        """Test that multiple messages are accepted."""
        now = datetime.now()
        messages = []
        for i in range(5):
            messages.append(ChatMessageResponse(
                id=i + 1,
                message_id=f"msg_{i + 1}",
                session_id=1,
                user_id=1,
                agent_type="finance",
                role=MessageRole.USER if i % 2 == 0 else MessageRole.AGENT,
                content=f"Message {i + 1}",
                metadata=None,
                created_at=now
            ))
        
        message_list = ChatMessageListResponse(
            messages=messages,
            total=5,
            page=1,
            page_size=10
        )
        assert len(message_list.messages) == 5
        assert message_list.total == 5


class TestMessageRoleEnum:
    """Tests for MessageRole enumeration type."""
    
    def test_message_role_values(self):
        """Test that MessageRole has correct values."""
        assert MessageRole.USER.value == "user"
        assert MessageRole.AGENT.value == "agent"
        assert MessageRole.SYSTEM.value == "system"
    
    def test_message_role_count(self):
        """Test that MessageRole has exactly 3 values."""
        assert len(MessageRole) == 3
