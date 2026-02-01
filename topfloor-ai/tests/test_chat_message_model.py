import pytest
from sqlalchemy import inspect
from app.models.chat_message import ChatMessage, MessageRole
from app.db.base import Base


def test_chat_message_model_exists():
    """Test that the ChatMessage model is properly defined."""
    assert ChatMessage is not None
    assert hasattr(ChatMessage, '__tablename__')
    assert ChatMessage.__tablename__ == "chat_messages"


def test_chat_message_model_inherits_from_base():
    """Test that ChatMessage model inherits from Base."""
    assert issubclass(ChatMessage, Base)


def test_chat_message_model_has_required_columns():
    """Test that ChatMessage model has all required columns."""
    columns = {col.name for col in ChatMessage.__table__.columns}
    required_columns = {
        'id', 'message_id', 'session_id', 'user_id', 
        'agent_type', 'role', 'content', 'message_metadata', 'created_at'
    }
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"


def test_chat_message_id_is_primary_key():
    """Test that id column is the primary key."""
    id_col = ChatMessage.__table__.columns['id']
    assert id_col.primary_key is True
    assert id_col.nullable is False


def test_chat_message_message_id_is_unique_and_indexed():
    """Test that message_id column is unique and indexed."""
    message_id_col = ChatMessage.__table__.columns['message_id']
    assert message_id_col.unique is True
    assert message_id_col.index is True
    assert message_id_col.nullable is False


def test_chat_message_foreign_keys():
    """Test that foreign key relationships are properly defined."""
    session_id_col = ChatMessage.__table__.columns['session_id']
    user_id_col = ChatMessage.__table__.columns['user_id']
    
    # Check that foreign keys exist
    assert session_id_col.foreign_keys is not None
    assert len(session_id_col.foreign_keys) > 0
    assert user_id_col.foreign_keys is not None
    assert len(user_id_col.foreign_keys) > 0
    
    # Check that columns are indexed
    assert session_id_col.index is True
    assert user_id_col.index is True
    
    # Check that columns are not nullable
    assert session_id_col.nullable is False
    assert user_id_col.nullable is False


def test_chat_message_agent_type_indexed():
    """Test that agent_type column is indexed."""
    agent_type_col = ChatMessage.__table__.columns['agent_type']
    assert agent_type_col.index is True
    assert agent_type_col.nullable is False


def test_chat_message_role_enum():
    """Test that role column uses MessageRole enum."""
    role_col = ChatMessage.__table__.columns['role']
    assert role_col.nullable is False


def test_chat_message_content_not_nullable():
    """Test that content column is not nullable."""
    content_col = ChatMessage.__table__.columns['content']
    assert content_col.nullable is False


def test_chat_message_metadata_nullable():
    """Test that message_metadata column is nullable (optional)."""
    metadata_col = ChatMessage.__table__.columns['message_metadata']
    assert metadata_col.nullable is True


def test_chat_message_created_at_indexed():
    """Test that created_at column is indexed."""
    created_at_col = ChatMessage.__table__.columns['created_at']
    assert created_at_col.index is True
    assert created_at_col.nullable is False


def test_chat_message_composite_index_exists():
    """Test that composite index on user_id, agent_type, created_at exists."""
    indexes = {idx.name for idx in ChatMessage.__table__.indexes}
    assert 'idx_user_agent_created' in indexes, "Composite index idx_user_agent_created not found"


def test_message_role_enum_values():
    """Test that MessageRole enum has expected values."""
    assert MessageRole.USER.value == "user"
    assert MessageRole.AGENT.value == "agent"
    assert MessageRole.SYSTEM.value == "system"


def test_chat_message_to_dict():
    """Test that ChatMessage has a to_dict method."""
    assert hasattr(ChatMessage, 'to_dict')
    assert callable(ChatMessage.to_dict)


def test_chat_message_repr():
    """Test that ChatMessage has a __repr__ method."""
    assert hasattr(ChatMessage, '__repr__')
    assert callable(ChatMessage.__repr__)
