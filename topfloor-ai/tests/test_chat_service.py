"""
Unit tests for ChatService
"""

import pytest
from app.models.user import User
from app.models.session import Session, SessionStatus
from app.models.chat_message import ChatMessage, MessageRole
from app.schemas.chat_message import ChatMessageCreate
from app.services.chat_service import ChatService


@pytest.fixture
def chat_service(db_session):
    """Create a ChatService instance with test database."""
    return ChatService(db_session)


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_session(db_session, test_user):
    """Create a test session."""
    session = Session(
        session_id="sess_test123",
        user_id=test_user.id,
        agent_type="finance",
        agent_name="Finance Agent",
        status=SessionStatus.ACTIVE
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@pytest.fixture
def sample_message_data(test_session):
    """Sample message data for testing."""
    return ChatMessageCreate(
        session_id=test_session.id,
        agent_type="finance",
        role=MessageRole.USER,
        content="Hello, can you help me with my budget?",
        metadata={"source": "web"}
    )


class TestCreateMessage:
    """Tests for message creation functionality"""
    
    def test_create_message_success(self, chat_service, test_user, sample_message_data):
        """Test successful message creation"""
        message = chat_service.create_message(test_user.id, sample_message_data)
        
        assert message is not None
        assert message.id is not None
        assert message.message_id is not None
        assert message.message_id.startswith("msg_")
        assert message.user_id == test_user.id
        assert message.session_id == sample_message_data.session_id
        assert message.agent_type == sample_message_data.agent_type
        assert message.role == sample_message_data.role
        assert message.content == sample_message_data.content
        assert message.message_metadata == sample_message_data.metadata
        assert message.created_at is not None
    
    def test_create_message_generates_unique_message_id(self, chat_service, test_user, sample_message_data):
        """Test that each message gets a unique message_id"""
        message1 = chat_service.create_message(test_user.id, sample_message_data)
        message2 = chat_service.create_message(test_user.id, sample_message_data)
        
        assert message1.message_id != message2.message_id
    
    def test_create_message_with_different_roles(self, chat_service, test_user, test_session):
        """Test creating messages with different roles"""
        for role in MessageRole:
            message_data = ChatMessageCreate(
                session_id=test_session.id,
                agent_type="finance",
                role=role,
                content=f"Message with {role.value} role"
            )
            message = chat_service.create_message(test_user.id, message_data)
            
            assert message.role == role
    
    def test_create_message_without_metadata(self, chat_service, test_user, test_session):
        """Test creating message without metadata"""
        message_data = ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="Hello"
        )
        message = chat_service.create_message(test_user.id, message_data)
        
        assert message.message_metadata is None
    
    def test_create_message_with_long_content(self, chat_service, test_user, test_session):
        """Test creating message with long content"""
        long_content = "x" * 10000
        message_data = ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content=long_content
        )
        message = chat_service.create_message(test_user.id, message_data)
        
        assert message.content == long_content


class TestGetMessageById:
    """Tests for retrieving messages by ID"""
    
    def test_get_message_by_id_existing_message(self, chat_service, test_user, sample_message_data):
        """Test retrieving an existing message by database ID"""
        created_message = chat_service.create_message(test_user.id, sample_message_data)
        
        retrieved_message = chat_service.get_message_by_id(created_message.id)
        
        assert retrieved_message is not None
        assert retrieved_message.id == created_message.id
        assert retrieved_message.content == created_message.content
    
    def test_get_message_by_id_with_user_filter(self, chat_service, test_user, sample_message_data):
        """Test retrieving message with user_id filter"""
        created_message = chat_service.create_message(test_user.id, sample_message_data)
        
        retrieved_message = chat_service.get_message_by_id(created_message.id, user_id=test_user.id)
        
        assert retrieved_message is not None
        assert retrieved_message.user_id == test_user.id
    
    def test_get_message_by_id_wrong_user_returns_none(self, chat_service, test_user, sample_message_data):
        """Test that retrieving message with wrong user_id returns None"""
        created_message = chat_service.create_message(test_user.id, sample_message_data)
        
        retrieved_message = chat_service.get_message_by_id(created_message.id, user_id=99999)
        
        assert retrieved_message is None
    
    def test_get_message_by_id_nonexistent_message(self, chat_service):
        """Test retrieving a non-existent message returns None"""
        retrieved_message = chat_service.get_message_by_id(99999)
        
        assert retrieved_message is None


class TestGetMessageByMessageId:
    """Tests for retrieving messages by message_id string"""
    
    def test_get_message_by_message_id_existing_message(self, chat_service, test_user, sample_message_data):
        """Test retrieving an existing message by message_id string"""
        created_message = chat_service.create_message(test_user.id, sample_message_data)
        
        retrieved_message = chat_service.get_message_by_message_id(created_message.message_id)
        
        assert retrieved_message is not None
        assert retrieved_message.message_id == created_message.message_id
        assert retrieved_message.id == created_message.id
    
    def test_get_message_by_message_id_with_user_filter(self, chat_service, test_user, sample_message_data):
        """Test retrieving message by message_id with user filter"""
        created_message = chat_service.create_message(test_user.id, sample_message_data)
        
        retrieved_message = chat_service.get_message_by_message_id(created_message.message_id, user_id=test_user.id)
        
        assert retrieved_message is not None
    
    def test_get_message_by_message_id_nonexistent_message(self, chat_service):
        """Test retrieving non-existent message by message_id returns None"""
        retrieved_message = chat_service.get_message_by_message_id("msg_nonexistent")
        
        assert retrieved_message is None


class TestGetMessagesBySession:
    """Tests for retrieving messages by session"""
    
    def test_get_messages_by_session_returns_session_messages(self, chat_service, test_user, test_session):
        """Test getting all messages for a session"""
        message1 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="First message"
        ))
        message2 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.AGENT,
            content="Second message"
        ))
        
        messages, total = chat_service.get_messages_by_session(test_session.id, test_user.id)
        
        assert total == 2
        assert len(messages) == 2
        # Messages should be in chronological order
        assert messages[0].id == message1.id
        assert messages[1].id == message2.id
    
    def test_get_messages_by_session_pagination(self, chat_service, test_user, test_session):
        """Test pagination of messages by session"""
        # Create 5 messages
        for i in range(5):
            chat_service.create_message(test_user.id, ChatMessageCreate(
                session_id=test_session.id,
                agent_type="finance",
                role=MessageRole.USER,
                content=f"Message {i + 1}"
            ))
        
        # Get first page (2 items)
        page1_messages, total = chat_service.get_messages_by_session(
            test_session.id, test_user.id, skip=0, limit=2
        )
        
        assert total == 5
        assert len(page1_messages) == 2
        
        # Get second page (2 items)
        page2_messages, _ = chat_service.get_messages_by_session(
            test_session.id, test_user.id, skip=2, limit=2
        )
        
        assert len(page2_messages) == 2
        assert page1_messages[0].id != page2_messages[0].id
    
    def test_get_messages_by_session_empty_session(self, chat_service, test_user, test_session):
        """Test getting messages for session with no messages"""
        messages, total = chat_service.get_messages_by_session(test_session.id, test_user.id)
        
        assert total == 0
        assert len(messages) == 0
    
    def test_get_messages_by_session_ordered_chronologically(self, chat_service, test_user, test_session):
        """Test that messages are ordered chronologically (oldest first)"""
        message1 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="First"
        ))
        message2 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.AGENT,
            content="Second"
        ))
        message3 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="Third"
        ))
        
        messages, _ = chat_service.get_messages_by_session(test_session.id, test_user.id)
        
        # Oldest should be first
        assert messages[0].id == message1.id
        assert messages[1].id == message2.id
        assert messages[2].id == message3.id


class TestGetMessagesByAgent:
    """Tests for retrieving messages by agent type"""
    
    def test_get_messages_by_agent_returns_agent_messages(self, chat_service, test_user, test_session, db_session):
        """Test getting all messages for an agent type"""
        # Create messages for finance agent
        finance_msg = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="Finance question"
        ))
        
        # Create session and message for researcher agent
        researcher_session = Session(
            session_id="sess_researcher",
            user_id=test_user.id,
            agent_type="researcher",
            agent_name="Researcher Agent",
            status=SessionStatus.ACTIVE
        )
        db_session.add(researcher_session)
        db_session.commit()
        db_session.refresh(researcher_session)
        
        researcher_msg = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=researcher_session.id,
            agent_type="researcher",
            role=MessageRole.USER,
            content="Research question"
        ))
        
        messages, total = chat_service.get_messages_by_agent(test_user.id, "finance")
        
        assert total == 1
        assert len(messages) == 1
        assert messages[0].id == finance_msg.id
    
    def test_get_messages_by_agent_pagination(self, chat_service, test_user, test_session):
        """Test pagination of messages by agent"""
        # Create 5 messages
        for i in range(5):
            chat_service.create_message(test_user.id, ChatMessageCreate(
                session_id=test_session.id,
                agent_type="finance",
                role=MessageRole.USER,
                content=f"Message {i + 1}"
            ))
        
        # Get first page (2 items)
        page1_messages, total = chat_service.get_messages_by_agent(
            test_user.id, "finance", skip=0, limit=2
        )
        
        assert total == 5
        assert len(page1_messages) == 2
    
    def test_get_messages_by_agent_ordered_by_created_desc(self, chat_service, test_user, test_session):
        """Test that messages are ordered by creation time (newest first)"""
        message1 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="First"
        ))
        message2 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.AGENT,
            content="Second"
        ))
        message3 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="Third"
        ))
        
        messages, _ = chat_service.get_messages_by_agent(test_user.id, "finance")
        
        # Newest should be first
        assert messages[0].id == message3.id
        assert messages[1].id == message2.id
        assert messages[2].id == message1.id


class TestGetRecentMessages:
    """Tests for getting recent messages"""
    
    def test_get_recent_messages_returns_recent_messages(self, chat_service, test_user, test_session):
        """Test getting recent messages for a user"""
        for i in range(3):
            chat_service.create_message(test_user.id, ChatMessageCreate(
                session_id=test_session.id,
                agent_type="finance",
                role=MessageRole.USER,
                content=f"Message {i + 1}"
            ))
        
        messages = chat_service.get_recent_messages(test_user.id, limit=2)
        
        assert len(messages) == 2
    
    def test_get_recent_messages_filter_by_agent(self, chat_service, test_user, test_session, db_session):
        """Test filtering recent messages by agent type"""
        # Create finance message
        finance_msg = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="Finance message"
        ))
        
        # Create researcher session and message
        researcher_session = Session(
            session_id="sess_researcher",
            user_id=test_user.id,
            agent_type="researcher",
            agent_name="Researcher Agent",
            status=SessionStatus.ACTIVE
        )
        db_session.add(researcher_session)
        db_session.commit()
        db_session.refresh(researcher_session)
        
        researcher_msg = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=researcher_session.id,
            agent_type="researcher",
            role=MessageRole.USER,
            content="Research message"
        ))
        
        messages = chat_service.get_recent_messages(test_user.id, agent_type="finance")
        
        assert len(messages) == 1
        assert messages[0].id == finance_msg.id
    
    def test_get_recent_messages_ordered_by_created_desc(self, chat_service, test_user, test_session):
        """Test that recent messages are ordered by creation time (newest first)"""
        message1 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="First"
        ))
        message2 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.AGENT,
            content="Second"
        ))
        
        messages = chat_service.get_recent_messages(test_user.id)
        
        # Newest should be first
        assert messages[0].id == message2.id
        assert messages[1].id == message1.id


class TestGetConversationHistory:
    """Tests for getting conversation history"""
    
    def test_get_conversation_history_for_agent(self, chat_service, test_user, test_session):
        """Test getting conversation history for a specific agent"""
        message1 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="First message"
        ))
        message2 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.AGENT,
            content="Second message"
        ))
        
        messages, total = chat_service.get_conversation_history(test_user.id, "finance")
        
        assert total == 2
        assert len(messages) == 2
        # Should be in chronological order
        assert messages[0].id == message1.id
        assert messages[1].id == message2.id
    
    def test_get_conversation_history_filter_by_session(self, chat_service, test_user, test_session, db_session):
        """Test filtering conversation history by session"""
        # Create messages in first session
        msg1 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="Session 1 message"
        ))
        
        # Create second session and message
        session2 = Session(
            session_id="sess_test456",
            user_id=test_user.id,
            agent_type="finance",
            agent_name="Finance Agent",
            status=SessionStatus.ACTIVE
        )
        db_session.add(session2)
        db_session.commit()
        db_session.refresh(session2)
        
        msg2 = chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=session2.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="Session 2 message"
        ))
        
        messages, total = chat_service.get_conversation_history(
            test_user.id, "finance", session_id=test_session.id
        )
        
        assert total == 1
        assert messages[0].id == msg1.id
    
    def test_get_conversation_history_pagination(self, chat_service, test_user, test_session):
        """Test pagination of conversation history"""
        # Create 5 messages
        for i in range(5):
            chat_service.create_message(test_user.id, ChatMessageCreate(
                session_id=test_session.id,
                agent_type="finance",
                role=MessageRole.USER,
                content=f"Message {i + 1}"
            ))
        
        # Get first page (2 items)
        page1_messages, total = chat_service.get_conversation_history(
            test_user.id, "finance", skip=0, limit=2
        )
        
        assert total == 5
        assert len(page1_messages) == 2


class TestDeleteMessage:
    """Tests for deleting messages"""
    
    def test_delete_message_success(self, chat_service, test_user, sample_message_data):
        """Test successful message deletion"""
        message = chat_service.create_message(test_user.id, sample_message_data)
        
        result = chat_service.delete_message(message.id, test_user.id)
        
        assert result is True
        
        # Verify message is deleted
        deleted_message = chat_service.get_message_by_id(message.id)
        assert deleted_message is None
    
    def test_delete_message_wrong_user_returns_false(self, chat_service, test_user, sample_message_data):
        """Test that deleting message with wrong user_id returns False"""
        message = chat_service.create_message(test_user.id, sample_message_data)
        
        result = chat_service.delete_message(message.id, 99999)
        
        assert result is False
        
        # Verify message still exists
        existing_message = chat_service.get_message_by_id(message.id)
        assert existing_message is not None
    
    def test_delete_message_nonexistent_message_returns_false(self, chat_service, test_user):
        """Test that deleting non-existent message returns False"""
        result = chat_service.delete_message(99999, test_user.id)
        
        assert result is False


class TestDeleteSessionMessages:
    """Tests for deleting all messages in a session"""
    
    def test_delete_session_messages_success(self, chat_service, test_user, test_session):
        """Test successful deletion of all session messages"""
        # Create 3 messages
        for i in range(3):
            chat_service.create_message(test_user.id, ChatMessageCreate(
                session_id=test_session.id,
                agent_type="finance",
                role=MessageRole.USER,
                content=f"Message {i + 1}"
            ))
        
        count = chat_service.delete_session_messages(test_session.id, test_user.id)
        
        assert count == 3
        
        # Verify messages are deleted
        messages, total = chat_service.get_messages_by_session(test_session.id, test_user.id)
        assert total == 0
    
    def test_delete_session_messages_empty_session(self, chat_service, test_user, test_session):
        """Test deleting messages from empty session"""
        count = chat_service.delete_session_messages(test_session.id, test_user.id)
        
        assert count == 0


class TestCountMessages:
    """Tests for counting messages"""
    
    def test_count_messages_by_agent(self, chat_service, test_user, test_session):
        """Test counting messages for a specific agent"""
        # Create 3 messages
        for i in range(3):
            chat_service.create_message(test_user.id, ChatMessageCreate(
                session_id=test_session.id,
                agent_type="finance",
                role=MessageRole.USER,
                content=f"Message {i + 1}"
            ))
        
        count = chat_service.count_messages_by_agent(test_user.id, "finance")
        
        assert count == 3
    
    def test_count_messages_by_session(self, chat_service, test_user, test_session):
        """Test counting messages for a specific session"""
        # Create 2 messages
        for i in range(2):
            chat_service.create_message(test_user.id, ChatMessageCreate(
                session_id=test_session.id,
                agent_type="finance",
                role=MessageRole.USER,
                content=f"Message {i + 1}"
            ))
        
        count = chat_service.count_messages_by_session(test_session.id, test_user.id)
        
        assert count == 2


class TestSearchMessages:
    """Tests for searching messages"""
    
    def test_search_messages_by_content(self, chat_service, test_user, test_session):
        """Test searching messages by content"""
        chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="Can you help me with my budget?"
        ))
        chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.AGENT,
            content="Sure, I can help with budgeting."
        ))
        chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="What about investments?"
        ))
        
        messages, total = chat_service.search_messages(test_user.id, "budget")
        
        assert total == 2
        assert len(messages) == 2
    
    def test_search_messages_case_insensitive(self, chat_service, test_user, test_session):
        """Test that search is case insensitive"""
        chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="BUDGET planning"
        ))
        
        messages, total = chat_service.search_messages(test_user.id, "budget")
        
        assert total == 1
    
    def test_search_messages_filter_by_agent(self, chat_service, test_user, test_session, db_session):
        """Test filtering search results by agent type"""
        # Create finance message with "budget"
        chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="Budget planning"
        ))
        
        # Create researcher session and message with "budget"
        researcher_session = Session(
            session_id="sess_researcher",
            user_id=test_user.id,
            agent_type="researcher",
            agent_name="Researcher Agent",
            status=SessionStatus.ACTIVE
        )
        db_session.add(researcher_session)
        db_session.commit()
        db_session.refresh(researcher_session)
        
        chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=researcher_session.id,
            agent_type="researcher",
            role=MessageRole.USER,
            content="Research budget"
        ))
        
        messages, total = chat_service.search_messages(test_user.id, "budget", agent_type="finance")
        
        assert total == 1
        assert messages[0].agent_type == "finance"
    
    def test_search_messages_pagination(self, chat_service, test_user, test_session):
        """Test pagination of search results"""
        # Create 5 messages with "test"
        for i in range(5):
            chat_service.create_message(test_user.id, ChatMessageCreate(
                session_id=test_session.id,
                agent_type="finance",
                role=MessageRole.USER,
                content=f"Test message {i + 1}"
            ))
        
        # Get first page (2 items)
        page1_messages, total = chat_service.search_messages(
            test_user.id, "test", skip=0, limit=2
        )
        
        assert total == 5
        assert len(page1_messages) == 2
    
    def test_search_messages_no_results(self, chat_service, test_user, test_session):
        """Test search with no matching results"""
        chat_service.create_message(test_user.id, ChatMessageCreate(
            session_id=test_session.id,
            agent_type="finance",
            role=MessageRole.USER,
            content="Hello world"
        ))
        
        messages, total = chat_service.search_messages(test_user.id, "nonexistent")
        
        assert total == 0
        assert len(messages) == 0
