"""
Tests for Session Service
"""

import pytest
from sqlalchemy.orm import Session as DBSession

from app.models.session import Session, SessionStatus
from app.models.user import User
from app.schemas.session import SessionCreate, SessionUpdate
from app.services.session_service import SessionService
from app.core.security import hash_password


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
def test_session(db_session: DBSession, test_user: User) -> Session:
    """Create a test session"""
    session_data = SessionCreate(
        agent_type="finance",
        agent_name="finance",
        title="Test Session",
        description="A test session"
    )
    return SessionService.create_session(db_session, test_user.id, session_data)


class TestSessionService:
    """Test suite for SessionService"""
    
    def test_generate_session_id(self):
        """Test session ID generation"""
        session_id = SessionService.generate_session_id()
        assert session_id.startswith("sess_")
        assert len(session_id) == 21  # "sess_" + 16 hex chars
    
    def test_create_session(self, db_session: DBSession, test_user: User):
        """Test creating a new session"""
        session_data = SessionCreate(
            agent_type="researcher",
            agent_name="researcher",
            title="Research Session",
            description="Testing research agent"
        )
        
        session = SessionService.create_session(db_session, test_user.id, session_data)
        
        assert session.id is not None
        assert session.session_id.startswith("sess_")
        assert session.user_id == test_user.id
        assert session.agent_type == "researcher"
        assert session.agent_name == "researcher"
        assert session.title == "Research Session"
        assert session.description == "Testing research agent"
        assert session.status == SessionStatus.ACTIVE
        assert session.created_at is not None
        assert session.updated_at is not None
        assert session.archived_at is None
    
    def test_get_session_by_id(self, db_session: DBSession, test_session: Session, test_user: User):
        """Test retrieving session by session_id"""
        retrieved = SessionService.get_session_by_id(
            db_session,
            test_session.session_id,
            test_user.id
        )
        
        assert retrieved is not None
        assert retrieved.id == test_session.id
        assert retrieved.session_id == test_session.session_id
    
    def test_get_session_by_id_wrong_user(self, db_session: DBSession, test_session: Session):
        """Test that getting session with wrong user_id returns None"""
        retrieved = SessionService.get_session_by_id(
            db_session,
            test_session.session_id,
            user_id=99999  # Non-existent user
        )
        
        assert retrieved is None
    
    def test_get_session_by_db_id(self, db_session: DBSession, test_session: Session, test_user: User):
        """Test retrieving session by database ID"""
        retrieved = SessionService.get_session_by_db_id(
            db_session,
            test_session.id,
            test_user.id
        )
        
        assert retrieved is not None
        assert retrieved.id == test_session.id
    
    def test_update_session_title(self, db_session: DBSession, test_session: Session, test_user: User):
        """Test updating session title"""
        update_data = SessionUpdate(title="Updated Title")
        
        updated = SessionService.update_session(
            db_session,
            test_session.session_id,
            test_user.id,
            update_data
        )
        
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.description == test_session.description  # Unchanged
    
    def test_update_session_description(self, db_session: DBSession, test_session: Session, test_user: User):
        """Test updating session description"""
        update_data = SessionUpdate(description="New description")
        
        updated = SessionService.update_session(
            db_session,
            test_session.session_id,
            test_user.id,
            update_data
        )
        
        assert updated is not None
        assert updated.description == "New description"
    
    def test_update_session_status(self, db_session: DBSession, test_session: Session, test_user: User):
        """Test updating session status"""
        update_data = SessionUpdate(status=SessionStatus.ARCHIVED)
        
        updated = SessionService.update_session(
            db_session,
            test_session.session_id,
            test_user.id,
            update_data
        )
        
        assert updated is not None
        assert updated.status == SessionStatus.ARCHIVED
        assert updated.archived_at is not None
    
    def test_archive_session(self, db_session: DBSession, test_session: Session, test_user: User):
        """Test archiving a session"""
        archived = SessionService.archive_session(
            db_session,
            test_session.session_id,
            test_user.id
        )
        
        assert archived is not None
        assert archived.status == SessionStatus.ARCHIVED
        assert archived.archived_at is not None
    
    def test_mark_session_failed(self, db_session: DBSession, test_session: Session, test_user: User):
        """Test marking session as failed"""
        failed = SessionService.mark_session_failed(
            db_session,
            test_session.session_id,
            test_user.id
        )
        
        assert failed is not None
        assert failed.status == SessionStatus.FAILED
    
    def test_list_user_sessions(self, db_session: DBSession, test_user: User):
        """Test listing user sessions"""
        # Create multiple sessions
        for i in range(5):
            session_data = SessionCreate(
                agent_type="finance" if i % 2 == 0 else "researcher",
                agent_name="finance" if i % 2 == 0 else "researcher",
                title=f"Session {i}"
            )
            SessionService.create_session(db_session, test_user.id, session_data)
        
        # List all sessions
        sessions, total = SessionService.list_user_sessions(db_session, test_user.id)
        
        assert len(sessions) == 5
        assert total == 5
    
    def test_list_user_sessions_with_status_filter(self, db_session: DBSession, test_user: User):
        """Test listing sessions with status filter"""
        # Create sessions with different statuses
        for i in range(3):
            session_data = SessionCreate(
                agent_type="finance",
                agent_name="finance",
                title=f"Session {i}"
            )
            session = SessionService.create_session(db_session, test_user.id, session_data)
            
            if i == 1:
                SessionService.archive_session(db_session, session.session_id, test_user.id)
        
        # List only active sessions
        sessions, total = SessionService.list_user_sessions(
            db_session,
            test_user.id,
            status=SessionStatus.ACTIVE
        )
        
        assert len(sessions) == 2
        assert total == 2
        assert all(s.status == SessionStatus.ACTIVE for s in sessions)
    
    def test_list_user_sessions_with_agent_type_filter(self, db_session: DBSession, test_user: User):
        """Test listing sessions with agent type filter"""
        # Create sessions with different agent types
        for agent_type in ["finance", "researcher", "finance"]:
            session_data = SessionCreate(
                agent_type=agent_type,
                agent_name=agent_type,
                title=f"{agent_type} session"
            )
            SessionService.create_session(db_session, test_user.id, session_data)
        
        # List only finance sessions
        sessions, total = SessionService.list_user_sessions(
            db_session,
            test_user.id,
            agent_type="finance"
        )
        
        assert len(sessions) == 2
        assert total == 2
        assert all(s.agent_type == "finance" for s in sessions)
    
    def test_list_user_sessions_pagination(self, db_session: DBSession, test_user: User):
        """Test session list pagination"""
        # Create 25 sessions
        for i in range(25):
            session_data = SessionCreate(
                agent_type="finance",
                agent_name="finance",
                title=f"Session {i}"
            )
            SessionService.create_session(db_session, test_user.id, session_data)
        
        # Get first page
        sessions_page1, total = SessionService.list_user_sessions(
            db_session,
            test_user.id,
            page=1,
            page_size=10
        )
        
        assert len(sessions_page1) == 10
        assert total == 25
        
        # Get second page
        sessions_page2, _ = SessionService.list_user_sessions(
            db_session,
            test_user.id,
            page=2,
            page_size=10
        )
        
        assert len(sessions_page2) == 10
        
        # Verify pages are different
        page1_ids = {s.id for s in sessions_page1}
        page2_ids = {s.id for s in sessions_page2}
        assert page1_ids.isdisjoint(page2_ids)
    
    def test_delete_session(self, db_session: DBSession, test_session: Session, test_user: User):
        """Test deleting a session"""
        session_id = test_session.session_id
        
        # Delete session
        result = SessionService.delete_session(db_session, session_id, test_user.id)
        assert result is True
        
        # Verify it's deleted
        retrieved = SessionService.get_session_by_id(db_session, session_id, test_user.id)
        assert retrieved is None
    
    def test_delete_nonexistent_session(self, db_session: DBSession, test_user: User):
        """Test deleting a non-existent session"""
        result = SessionService.delete_session(db_session, "sess_nonexistent", test_user.id)
        assert result is False
