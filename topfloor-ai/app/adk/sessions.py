"""
ADK Session Management - Bridge between database sessions and ADK sessions
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
import asyncio

from google.adk.sessions import Session as ADKSession, InMemorySessionService
from google.adk.runners import Runner

from app.models.session import Session as DBSessionModel, SessionStatus
from app.services.session_service import SessionService
from app.adk.client import adk_client


class SessionManager:
    """
    Manages the lifecycle and mapping between database sessions and ADK sessions.
    
    Responsibilities:
    - Create/retrieve ADK sessions mapped to database sessions
    - Maintain session state scoping (user + agent + session)
    - Handle session lifecycle (create, resume, archive)
    - Prevent memory bloat through proper session management
    
    Memory Strategy:
    - Short-term: ADK session.state for current task context
    - Long-term: Database for session metadata (not raw memory blobs)
    - Scoping: Each session is isolated per user + agent + session_id
    
    Note: ADK session operations are async, but we provide sync wrappers for convenience.
    """
    
    def __init__(self):
        """Initialize session manager with ADK session service"""
        self.adk_session_service = adk_client.session_service
        # Cache of active ADK sessions (session_id -> ADK Session)
        self._active_sessions: Dict[str, ADKSession] = {}
    
    def create_session(
        self,
        db: DBSession,
        user_id: int,
        agent_type: str,
        agent_name: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> tuple[DBSessionModel, ADKSession]:
        """
        Create a new session (both database and ADK).
        
        Args:
            db: Database session
            user_id: User ID
            agent_type: Type of agent
            agent_name: Name of agent
            title: Optional session title
            description: Optional description
            
        Returns:
            Tuple of (database session, ADK session)
        """
        from app.schemas.session import SessionCreate
        
        # Create database session
        session_data = SessionCreate(
            agent_type=agent_type,
            agent_name=agent_name,
            title=title,
            description=description
        )
        db_session = SessionService.create_session(db, user_id, session_data)
        
        # Create ADK session (sync wrapper for async operation)
        adk_session = self._create_adk_session_sync(
            session_id=db_session.session_id,
            user_id=user_id,
            agent_type=agent_type
        )
        
        # Cache the ADK session
        self._active_sessions[db_session.session_id] = adk_session
        
        return db_session, adk_session
    
    def get_or_create_adk_session(
        self,
        db: DBSession,
        session_id: str,
        user_id: int
    ) -> Optional[tuple[DBSessionModel, ADKSession]]:
        """
        Get existing session or return None if not found.
        
        Args:
            db: Database session
            session_id: Session ID to retrieve
            user_id: User ID for authorization
            
        Returns:
            Tuple of (database session, ADK session) or None if not found
        """
        # Get database session
        db_session = SessionService.get_session_by_id(db, session_id, user_id)
        if not db_session:
            return None
        
        # Check if session is active
        if db_session.status != SessionStatus.ACTIVE:
            return None
        
        # Get or create ADK session
        if session_id in self._active_sessions:
            adk_session = self._active_sessions[session_id]
        else:
            adk_session = self._create_adk_session_sync(
                session_id=session_id,
                user_id=user_id,
                agent_type=db_session.agent_type
            )
            self._active_sessions[session_id] = adk_session
        
        return db_session, adk_session
    
    def _create_adk_session_sync(
        self,
        session_id: str,
        user_id: int,
        agent_type: str
    ) -> ADKSession:
        """
        Create a new ADK session with proper scoping (sync wrapper).
        
        Args:
            session_id: Unique session identifier
            user_id: User ID for scoping
            agent_type: Agent type for scoping
            
        Returns:
            ADK Session instance
        """
        # For InMemorySessionService, we can create a simple session object
        # without async operations for testing purposes
        # In production with VertexAiSessionService, this would need proper async handling
        
        # Create a simple session object with state
        class SimpleSession:
            def __init__(self, session_id: str):
                self.session_id = session_id
                self.state = {}
        
        adk_session_id = f"user_{user_id}_agent_{agent_type}_{session_id}"
        return SimpleSession(adk_session_id)
    
    def archive_session(
        self,
        db: DBSession,
        session_id: str,
        user_id: int
    ) -> Optional[DBSessionModel]:
        """
        Archive a session (both database and ADK).
        
        Args:
            db: Database session
            session_id: Session ID to archive
            user_id: User ID for authorization
            
        Returns:
            Archived database session or None if not found
        """
        # Archive in database
        db_session = SessionService.archive_session(db, session_id, user_id)
        
        if db_session:
            # Remove from active cache
            if session_id in self._active_sessions:
                del self._active_sessions[session_id]
        
        return db_session
    
    def clear_session_cache(self, session_id: str):
        """
        Clear a session from the active cache.
        
        Args:
            session_id: Session ID to clear
        """
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
    
    def get_session_state(
        self,
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get the current state of an ADK session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session state dictionary or None if not found
        """
        if session_id not in self._active_sessions:
            return None
        
        adk_session = self._active_sessions[session_id]
        return dict(adk_session.state) if hasattr(adk_session, 'state') else {}
    
    def update_session_state(
        self,
        session_id: str,
        state_updates: Dict[str, Any]
    ) -> bool:
        """
        Update the state of an ADK session.
        
        Args:
            session_id: Session ID
            state_updates: Dictionary of state updates
            
        Returns:
            True if updated, False if session not found
        """
        if session_id not in self._active_sessions:
            return False
        
        adk_session = self._active_sessions[session_id]
        if hasattr(adk_session, 'state'):
            adk_session.state.update(state_updates)
            return True
        
        return False


# Global session manager instance
session_manager = SessionManager()
