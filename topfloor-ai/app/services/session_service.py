"""
Session Service - Business logic for session management
"""

from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from app.models.session import Session, SessionStatus
from app.schemas.session import SessionCreate, SessionUpdate


class SessionService:
    """
    Service for managing agent sessions.
    
    Responsibilities:
    - Create new sessions
    - Retrieve sessions by ID or user
    - Update session status and metadata
    - Archive sessions
    - List user sessions with pagination
    """
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate a unique session ID"""
        return f"sess_{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def create_session(
        db: DBSession,
        user_id: int,
        session_data: SessionCreate
    ) -> Session:
        """
        Create a new session.
        
        Args:
            db: Database session
            user_id: ID of the user creating the session
            session_data: Session creation data
            
        Returns:
            Created session
        """
        session = Session(
            session_id=SessionService.generate_session_id(),
            user_id=user_id,
            agent_type=session_data.agent_type,
            agent_name=session_data.agent_name,
            title=session_data.title,
            description=session_data.description,
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def get_session_by_id(
        db: DBSession,
        session_id: str,
        user_id: Optional[int] = None
    ) -> Optional[Session]:
        """
        Get session by session_id.
        
        Args:
            db: Database session
            session_id: Session ID to retrieve
            user_id: Optional user ID for authorization check
            
        Returns:
            Session if found, None otherwise
        """
        query = db.query(Session).filter(Session.session_id == session_id)
        
        if user_id is not None:
            query = query.filter(Session.user_id == user_id)
        
        return query.first()
    
    @staticmethod
    def get_session_by_db_id(
        db: DBSession,
        id: int,
        user_id: Optional[int] = None
    ) -> Optional[Session]:
        """
        Get session by database ID.
        
        Args:
            db: Database session
            id: Database ID
            user_id: Optional user ID for authorization check
            
        Returns:
            Session if found, None otherwise
        """
        query = db.query(Session).filter(Session.id == id)
        
        if user_id is not None:
            query = query.filter(Session.user_id == user_id)
        
        return query.first()
    
    @staticmethod
    def update_session(
        db: DBSession,
        session_id: str,
        user_id: int,
        update_data: SessionUpdate
    ) -> Optional[Session]:
        """
        Update session metadata.
        
        Args:
            db: Database session
            session_id: Session ID to update
            user_id: User ID for authorization
            update_data: Update data
            
        Returns:
            Updated session if found, None otherwise
        """
        session = SessionService.get_session_by_id(db, session_id, user_id)
        
        if not session:
            return None
        
        # Update fields if provided
        if update_data.title is not None:
            session.title = update_data.title
        if update_data.description is not None:
            session.description = update_data.description
        if update_data.status is not None:
            session.status = update_data.status
            if update_data.status == SessionStatus.ARCHIVED:
                session.archived_at = datetime.now(timezone.utc)
        
        session.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def archive_session(
        db: DBSession,
        session_id: str,
        user_id: int
    ) -> Optional[Session]:
        """
        Archive a session.
        
        Args:
            db: Database session
            session_id: Session ID to archive
            user_id: User ID for authorization
            
        Returns:
            Archived session if found, None otherwise
        """
        update_data = SessionUpdate(status=SessionStatus.ARCHIVED)
        return SessionService.update_session(db, session_id, user_id, update_data)
    
    @staticmethod
    def mark_session_failed(
        db: DBSession,
        session_id: str,
        user_id: int
    ) -> Optional[Session]:
        """
        Mark a session as failed.
        
        Args:
            db: Database session
            session_id: Session ID to mark as failed
            user_id: User ID for authorization
            
        Returns:
            Updated session if found, None otherwise
        """
        update_data = SessionUpdate(status=SessionStatus.FAILED)
        return SessionService.update_session(db, session_id, user_id, update_data)
    
    @staticmethod
    def list_user_sessions(
        db: DBSession,
        user_id: int,
        status: Optional[SessionStatus] = None,
        agent_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Session], int]:
        """
        List sessions for a user with pagination.
        
        Args:
            db: Database session
            user_id: User ID to filter by
            status: Optional status filter
            agent_type: Optional agent type filter
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (sessions list, total count)
        """
        query = db.query(Session).filter(Session.user_id == user_id)
        
        # Apply filters
        if status is not None:
            query = query.filter(Session.status == status)
        if agent_type is not None:
            query = query.filter(Session.agent_type == agent_type)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        sessions = (
            query
            .order_by(desc(Session.updated_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        
        return sessions, total
    
    @staticmethod
    def delete_session(
        db: DBSession,
        session_id: str,
        user_id: int
    ) -> bool:
        """
        Delete a session (hard delete).
        
        Args:
            db: Database session
            session_id: Session ID to delete
            user_id: User ID for authorization
            
        Returns:
            True if deleted, False if not found
        """
        session = SessionService.get_session_by_id(db, session_id, user_id)
        
        if not session:
            return False
        
        db.delete(session)
        db.commit()
        
        return True
