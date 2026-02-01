"""
Chat Service - Business logic for chat message storage and retrieval
"""

from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, and_
from app.models.chat_message import ChatMessage, MessageRole
from app.schemas.chat_message import ChatMessageCreate
from typing import Optional, List
from datetime import datetime, timezone
import uuid


class ChatService:
    """Service for managing chat messages with CRUD operations"""
    
    def __init__(self, db: DBSession):
        self.db = db
    
    def create_message(self, user_id: int, message_data: ChatMessageCreate) -> ChatMessage:
        """
        Create a new chat message.
        
        Args:
            user_id: ID of the user creating the message
            message_data: Message creation data
            
        Returns:
            Created message object
            
        Raises:
            ValueError: If message creation fails
        """
        # Generate unique message_id
        message_id = f"msg_{uuid.uuid4().hex[:16]}"
        
        # Create message object
        db_message = ChatMessage(
            message_id=message_id,
            session_id=message_data.session_id,
            user_id=user_id,
            agent_type=message_data.agent_type,
            role=message_data.role,
            content=message_data.content,
            message_metadata=message_data.metadata,
            created_at=datetime.now(timezone.utc)
        )
        
        self.db.add(db_message)
        try:
            self.db.commit()
            self.db.refresh(db_message)
            return db_message
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Failed to create message: {str(e)}")
    
    def get_message_by_id(self, message_id: int, user_id: Optional[int] = None) -> Optional[ChatMessage]:
        """
        Get a message by its database ID.
        
        Args:
            message_id: Database ID of the message
            user_id: Optional user ID to filter by (for authorization)
            
        Returns:
            Message object if found, None otherwise
        """
        query = self.db.query(ChatMessage).filter(ChatMessage.id == message_id)
        
        if user_id is not None:
            query = query.filter(ChatMessage.user_id == user_id)
        
        return query.first()
    
    def get_message_by_message_id(self, message_id: str, user_id: Optional[int] = None) -> Optional[ChatMessage]:
        """
        Get a message by its unique message_id string.
        
        Args:
            message_id: Unique message_id string
            user_id: Optional user ID to filter by (for authorization)
            
        Returns:
            Message object if found, None otherwise
        """
        query = self.db.query(ChatMessage).filter(ChatMessage.message_id == message_id)
        
        if user_id is not None:
            query = query.filter(ChatMessage.user_id == user_id)
        
        return query.first()
    
    def get_messages_by_session(
        self,
        session_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ChatMessage], int]:
        """
        Get messages for a specific session with pagination.
        
        Args:
            session_id: Session ID to filter messages
            user_id: User ID (for authorization)
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of messages, total count)
        """
        # Build query
        query = self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.session_id == session_id,
                ChatMessage.user_id == user_id
            )
        )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering (chronological order)
        messages = query.order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
        
        return messages, total
    
    def get_messages_by_agent(
        self,
        user_id: int,
        agent_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ChatMessage], int]:
        """
        Get all messages for a specific agent type.
        
        Args:
            user_id: User ID to filter messages
            agent_type: Agent type to filter
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of messages, total count)
        """
        # Build query
        query = self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.user_id == user_id,
                ChatMessage.agent_type == agent_type
            )
        )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering (most recent first)
        messages = query.order_by(desc(ChatMessage.created_at)).offset(skip).limit(limit).all()
        
        return messages, total
    
    def get_recent_messages(
        self,
        user_id: int,
        agent_type: Optional[str] = None,
        limit: int = 50
    ) -> List[ChatMessage]:
        """
        Get recent messages for a user, optionally filtered by agent.
        
        Args:
            user_id: User ID to filter messages
            agent_type: Optional agent type filter
            limit: Maximum number of messages to return
            
        Returns:
            List of recent messages ordered by creation time (most recent first)
        """
        query = self.db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
        
        if agent_type is not None:
            query = query.filter(ChatMessage.agent_type == agent_type)
        
        messages = query.order_by(desc(ChatMessage.created_at)).limit(limit).all()
        
        return messages
    
    def get_conversation_history(
        self,
        user_id: int,
        agent_type: str,
        session_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[ChatMessage], int]:
        """
        Get conversation history for a user and agent, optionally filtered by session.
        
        Args:
            user_id: User ID to filter messages
            agent_type: Agent type to filter
            session_id: Optional session ID to filter
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of messages in chronological order, total count)
        """
        # Build query
        query = self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.user_id == user_id,
                ChatMessage.agent_type == agent_type
            )
        )
        
        if session_id is not None:
            query = query.filter(ChatMessage.session_id == session_id)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering (chronological order for conversation flow)
        messages = query.order_by(ChatMessage.created_at).offset(skip).limit(limit).all()
        
        return messages, total
    
    def delete_message(self, message_id: int, user_id: int) -> bool:
        """
        Delete a message.
        
        Args:
            message_id: Database ID of the message
            user_id: User ID (for authorization)
            
        Returns:
            True if message was deleted, False if not found
        """
        message = self.get_message_by_id(message_id, user_id)
        
        if message is None:
            return False
        
        self.db.delete(message)
        self.db.commit()
        
        return True
    
    def delete_session_messages(self, session_id: int, user_id: int) -> int:
        """
        Delete all messages for a session.
        
        Args:
            session_id: Session ID
            user_id: User ID (for authorization)
            
        Returns:
            Number of messages deleted
        """
        messages = self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.session_id == session_id,
                ChatMessage.user_id == user_id
            )
        ).all()
        
        count = len(messages)
        
        for message in messages:
            self.db.delete(message)
        
        self.db.commit()
        
        return count
    
    def count_messages_by_agent(self, user_id: int, agent_type: str) -> int:
        """
        Count total messages for a specific agent.
        
        Args:
            user_id: User ID to filter messages
            agent_type: Agent type to filter
            
        Returns:
            Total message count
        """
        return self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.user_id == user_id,
                ChatMessage.agent_type == agent_type
            )
        ).count()
    
    def count_messages_by_session(self, session_id: int, user_id: int) -> int:
        """
        Count total messages for a specific session.
        
        Args:
            session_id: Session ID to filter messages
            user_id: User ID (for authorization)
            
        Returns:
            Total message count
        """
        return self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.session_id == session_id,
                ChatMessage.user_id == user_id
            )
        ).count()
    
    def search_messages(
        self,
        user_id: int,
        search_term: str,
        agent_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[ChatMessage], int]:
        """
        Search messages by content.
        
        Args:
            user_id: User ID to filter messages
            search_term: Term to search for in message content
            agent_type: Optional agent type filter
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of matching messages, total count)
        """
        # Build query
        query = self.db.query(ChatMessage).filter(
            and_(
                ChatMessage.user_id == user_id,
                ChatMessage.content.ilike(f"%{search_term}%")
            )
        )
        
        if agent_type is not None:
            query = query.filter(ChatMessage.agent_type == agent_type)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination and ordering (most recent first)
        messages = query.order_by(desc(ChatMessage.created_at)).offset(skip).limit(limit).all()
        
        return messages, total
