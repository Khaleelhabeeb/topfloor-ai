"""
Tests for ADK Session Management
"""

import pytest
from sqlalchemy.orm import Session as DBSession

from app.models.user import User
from app.models.session import SessionStatus
from app.core.security import hash_password
from app.adk.sessions import SessionManager
from app.adk.memory import MemoryStrategy, MemoryScope


@pytest.fixture
def test_user(db_session: DBSession) -> User:
    """Create a test user"""
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpassword")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def session_manager():
    """Create a fresh session manager for each test"""
    return SessionManager()


class TestSessionManager:
    """Test suite for SessionManager"""
    
    def test_create_session(self, db_session: DBSession, test_user: User, session_manager: SessionManager):
        """Test creating a new session"""
        db_sess, adk_sess = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer",
            title="Test Session"
        )
        
        # Verify database session
        assert db_sess.id is not None
        assert db_sess.session_id.startswith("sess_")
        assert db_sess.user_id == test_user.id
        assert db_sess.agent_type == "developer"
        assert db_sess.status == SessionStatus.ACTIVE
        
        # Verify ADK session exists
        assert adk_sess is not None
        
        # Verify session is cached
        assert db_sess.session_id in session_manager._active_sessions
    
    def test_get_or_create_adk_session_existing(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test retrieving an existing session"""
        # Create session
        db_sess, adk_sess = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="researcher",
            agent_name="researcher"
        )
        
        # Retrieve the same session
        result = session_manager.get_or_create_adk_session(
            db=db_session,
            session_id=db_sess.session_id,
            user_id=test_user.id
        )
        
        assert result is not None
        retrieved_db_sess, retrieved_adk_sess = result
        
        # Verify it's the same session
        assert retrieved_db_sess.id == db_sess.id
        assert retrieved_db_sess.session_id == db_sess.session_id
    
    def test_get_or_create_adk_session_nonexistent(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test retrieving a non-existent session returns None"""
        result = session_manager.get_or_create_adk_session(
            db=db_session,
            session_id="sess_nonexistent",
            user_id=test_user.id
        )
        
        assert result is None
    
    def test_get_or_create_adk_session_archived(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test that archived sessions cannot be retrieved"""
        # Create and archive session
        db_sess, _ = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        session_manager.archive_session(
            db=db_session,
            session_id=db_sess.session_id,
            user_id=test_user.id
        )
        
        # Try to retrieve archived session
        result = session_manager.get_or_create_adk_session(
            db=db_session,
            session_id=db_sess.session_id,
            user_id=test_user.id
        )
        
        assert result is None
    
    def test_archive_session(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test archiving a session"""
        # Create session
        db_sess, _ = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        session_id = db_sess.session_id
        
        # Verify it's in cache
        assert session_id in session_manager._active_sessions
        
        # Archive session
        archived = session_manager.archive_session(
            db=db_session,
            session_id=session_id,
            user_id=test_user.id
        )
        
        assert archived is not None
        assert archived.status == SessionStatus.ARCHIVED
        
        # Verify it's removed from cache
        assert session_id not in session_manager._active_sessions
    
    def test_clear_session_cache(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test clearing session from cache"""
        # Create session
        db_sess, _ = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        session_id = db_sess.session_id
        
        # Verify it's in cache
        assert session_id in session_manager._active_sessions
        
        # Clear from cache
        session_manager.clear_session_cache(session_id)
        
        # Verify it's removed
        assert session_id not in session_manager._active_sessions
    
    def test_get_session_state(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test getting session state"""
        # Create session
        db_sess, adk_sess = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        # Initialize state
        MemoryStrategy.initialize_session_state(
            adk_sess,
            user_id=test_user.id,
            agent_type="developer"
        )
        
        # Get state
        state = session_manager.get_session_state(db_sess.session_id)
        
        assert state is not None
        assert state.get("user_id") == test_user.id
        assert state.get("agent_type") == "developer"
    
    def test_update_session_state(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test updating session state"""
        # Create session
        db_sess, adk_sess = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        # Initialize state
        MemoryStrategy.initialize_session_state(
            adk_sess,
            user_id=test_user.id,
            agent_type="developer"
        )
        
        # Update state
        result = session_manager.update_session_state(
            db_sess.session_id,
            {"custom_key": "custom_value"}
        )
        
        assert result is True
        
        # Verify update
        state = session_manager.get_session_state(db_sess.session_id)
        assert state.get("custom_key") == "custom_value"


class TestMemoryStrategy:
    """Test suite for MemoryStrategy"""
    
    def test_initialize_session_state(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test initializing session state"""
        _, adk_sess = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        MemoryStrategy.initialize_session_state(
            adk_sess,
            user_id=test_user.id,
            agent_type="developer",
            initial_context={"test_key": "test_value"}
        )
        
        assert adk_sess.state.get("user_id") == test_user.id
        assert adk_sess.state.get("agent_type") == "developer"
        assert adk_sess.state.get("test_key") == "test_value"
        assert "session_started_at" in adk_sess.state
        assert "task_context" in adk_sess.state
        assert "metadata" in adk_sess.state
    
    def test_update_task_context(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test updating task context"""
        _, adk_sess = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        MemoryStrategy.initialize_session_state(adk_sess, test_user.id, "developer")
        
        MemoryStrategy.update_task_context(
            adk_sess,
            {"current_task": "write_code", "language": "python"}
        )
        
        context = MemoryStrategy.get_task_context(adk_sess)
        assert context.get("current_task") == "write_code"
        assert context.get("language") == "python"
    
    def test_clear_task_context(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test clearing task context"""
        _, adk_sess = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        MemoryStrategy.initialize_session_state(adk_sess, test_user.id, "developer")
        MemoryStrategy.update_task_context(adk_sess, {"task": "test"})
        
        # Clear context
        MemoryStrategy.clear_task_context(adk_sess)
        
        context = MemoryStrategy.get_task_context(adk_sess)
        assert len(context) == 0
    
    def test_add_and_get_metadata(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test adding and retrieving metadata"""
        _, adk_sess = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        MemoryStrategy.initialize_session_state(adk_sess, test_user.id, "developer")
        
        MemoryStrategy.add_metadata(adk_sess, "last_action", "code_review")
        
        value = MemoryStrategy.get_metadata(adk_sess, "last_action")
        assert value == "code_review"
        
        # Test default value
        default_value = MemoryStrategy.get_metadata(adk_sess, "nonexistent", "default")
        assert default_value == "default"
    
    def test_get_session_summary(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test getting session summary"""
        _, adk_sess = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        MemoryStrategy.initialize_session_state(adk_sess, test_user.id, "developer")
        MemoryStrategy.update_task_context(adk_sess, {"task": "test"})
        MemoryStrategy.add_metadata(adk_sess, "key", "value")
        
        summary = MemoryStrategy.get_session_summary(adk_sess)
        
        assert summary.get("user_id") == test_user.id
        assert summary.get("agent_type") == "developer"
        assert "task_context_keys" in summary
        assert "metadata_keys" in summary
        assert "state_size_estimate" in summary
    
    def test_enforce_memory_limits(
        self,
        db_session: DBSession,
        test_user: User,
        session_manager: SessionManager
    ):
        """Test enforcing memory limits"""
        _, adk_sess = session_manager.create_session(
            db=db_session,
            user_id=test_user.id,
            agent_type="developer",
            agent_name="developer"
        )
        
        MemoryStrategy.initialize_session_state(adk_sess, test_user.id, "developer")
        
        # Add many items to task context
        for i in range(60):
            MemoryStrategy.update_task_context(adk_sess, {f"key_{i}": f"value_{i}"})
        
        # Enforce limits
        removed = MemoryStrategy.enforce_memory_limits(
            adk_sess,
            max_task_context_items=50
        )
        
        assert removed["task_context"] == 10
        
        # Verify size is limited
        context = MemoryStrategy.get_task_context(adk_sess)
        assert len(context) == 50


class TestMemoryScope:
    """Test suite for MemoryScope"""
    
    def test_create_scope_key(self):
        """Test creating a scope key"""
        key = MemoryScope.create_scope_key(
            user_id=123,
            agent_type="developer",
            session_id="sess_abc123"
        )
        
        assert key == "user_123:agent_developer:session_sess_abc123"
    
    def test_parse_scope_key(self):
        """Test parsing a scope key"""
        key = "user_123:agent_developer:session_sess_abc123"
        
        parsed = MemoryScope.parse_scope_key(key)
        
        assert parsed is not None
        assert parsed["user_id"] == "123"
        assert parsed["agent_type"] == "developer"
        assert parsed["session_id"] == "sess_abc123"
    
    def test_parse_invalid_scope_key(self):
        """Test parsing an invalid scope key"""
        parsed = MemoryScope.parse_scope_key("invalid_key")
        assert parsed is None
    
    def test_validate_scope(self):
        """Test scope validation"""
        assert MemoryScope.validate_scope(1, "developer", "sess_123") is True
        assert MemoryScope.validate_scope(0, "developer", "sess_123") is False
        assert MemoryScope.validate_scope(1, "", "sess_123") is False
        assert MemoryScope.validate_scope(1, "developer", "") is False
