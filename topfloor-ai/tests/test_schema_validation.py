"""
Comprehensive validation tests for all schemas.
Tests security validations including XSS prevention, SQL injection prevention,
and input sanitization as per NFR-6 requirements.
"""

import pytest
from pydantic import ValidationError
from app.schemas.task import TaskCreate, TaskUpdate, TaskPriority, TaskType
from app.schemas.chat_message import ChatMessageCreate, MessageRole
from app.schemas.artifact import ArtifactCreate
from app.schemas.session import SessionCreate, SessionUpdate
from app.schemas.user import UserCreate


class TestXSSPrevention:
    """Test XSS attack prevention in all schemas."""
    
    def test_task_title_xss_script_tag(self):
        """Test that script tags in task title are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(
                title="<script>alert('xss')</script>",
                agent_type="finance"
            )
        assert "potentially dangerous content" in str(exc_info.value)
    
    def test_task_description_xss_javascript(self):
        """Test that javascript: protocol in description is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(
                title="Valid Title",
                description="Click here: javascript:alert('xss')",
                agent_type="finance"
            )
        assert "potentially dangerous content" in str(exc_info.value)
    
    def test_task_description_xss_onclick(self):
        """Test that onclick handlers are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(
                title="Valid Title",
                description="<div onclick='alert(1)'>Click me</div>",
                agent_type="finance"
            )
        assert "potentially dangerous content" in str(exc_info.value)
    
    def test_session_title_xss_iframe(self):
        """Test that iframe tags in session title are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SessionCreate(
                agent_type="finance",
                agent_name="Finance Agent",
                title="<iframe src='evil.com'></iframe>"
            )
        assert "potentially dangerous content" in str(exc_info.value)
    
    def test_session_description_xss_object(self):
        """Test that object tags in session description are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SessionCreate(
                agent_type="finance",
                agent_name="Finance Agent",
                description="<object data='evil.swf'></object>"
            )
        assert "potentially dangerous content" in str(exc_info.value)


class TestAgentTypeValidation:
    """Test agent type validation across all schemas."""
    
    def test_task_invalid_agent_type_format(self):
        """Test that invalid agent type format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(
                title="Test Task",
                agent_type="Invalid-Agent"
            )
        assert "lowercase letters and underscores" in str(exc_info.value)
    
    def test_task_unknown_agent_type(self):
        """Test that unknown agent type is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(
                title="Test Task",
                agent_type="unknown_agent"
            )
        assert "Invalid agent type" in str(exc_info.value)
    
    def test_chat_message_valid_agent_types(self):
        """Test that all valid agent types are accepted."""
        valid_agents = ['orchestrator', 'team_lead', 'finance', 'data_analyst', 'researcher']
        
        for agent in valid_agents:
            message = ChatMessageCreate(
                session_id=1,
                agent_type=agent,
                role=MessageRole.USER,
                content="Test message"
            )
            assert message.agent_type == agent
    
    def test_artifact_invalid_agent_type(self):
        """Test that invalid agent type in artifact is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ArtifactCreate(
                agent_type="INVALID",
                file_name="test.pdf",
                file_type="pdf",
                file_path="/storage/test.pdf",
                file_size=1024
            )
        assert "lowercase letters and underscores" in str(exc_info.value)


class TestFileValidation:
    """Test file-related validation in artifact schemas."""
    
    def test_file_name_path_traversal(self):
        """Test that path traversal in file name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ArtifactCreate(
                agent_type="finance",
                file_name="../../../etc/passwd",
                file_type="pdf",
                file_path="/storage/test.pdf",
                file_size=1024
            )
        assert "path traversal" in str(exc_info.value)
    
    def test_file_name_invalid_characters(self):
        """Test that invalid characters in file name are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ArtifactCreate(
                agent_type="finance",
                file_name="test<script>.pdf",
                file_type="pdf",
                file_path="/storage/test.pdf",
                file_size=1024
            )
        assert "invalid characters" in str(exc_info.value)
    
    def test_file_type_not_allowed(self):
        """Test that disallowed file types are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ArtifactCreate(
                agent_type="finance",
                file_name="malware.exe",
                file_type="exe",
                file_path="/storage/malware.exe",
                file_size=1024
            )
        assert "not allowed" in str(exc_info.value)
    
    def test_file_size_exceeds_limit(self):
        """Test that files over 100MB are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ArtifactCreate(
                agent_type="finance",
                file_name="huge.pdf",
                file_type="pdf",
                file_path="/storage/huge.pdf",
                file_size=200_000_000  # 200MB
            )
        assert "less than or equal to 100000000" in str(exc_info.value)
    
    def test_mime_type_invalid_format(self):
        """Test that invalid MIME type format is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ArtifactCreate(
                agent_type="finance",
                file_name="test.pdf",
                file_type="pdf",
                file_path="/storage/test.pdf",
                file_size=1024,
                mime_type="not-a-mime-type"
            )
        assert "Invalid MIME type format" in str(exc_info.value)
    
    def test_valid_mime_types(self):
        """Test that valid MIME types are accepted."""
        valid_mimes = [
            "application/pdf",
            "image/png",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        for mime in valid_mimes:
            artifact = ArtifactCreate(
                agent_type="finance",
                file_name="test.pdf",
                file_type="pdf",
                file_path="/storage/test.pdf",
                file_size=1024,
                mime_type=mime
            )
            assert artifact.mime_type == mime.lower()


class TestPasswordValidation:
    """Test password strength validation."""
    
    def test_password_missing_uppercase(self):
        """Test that password without uppercase is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="password123!"
            )
        assert "uppercase letter" in str(exc_info.value)
    
    def test_password_missing_lowercase(self):
        """Test that password without lowercase is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="PASSWORD123!"
            )
        assert "lowercase letter" in str(exc_info.value)
    
    def test_password_missing_digit(self):
        """Test that password without digit is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="Password!"
            )
        assert "digit" in str(exc_info.value)
    
    def test_password_missing_special_char(self):
        """Test that password without special character is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="Password123"
            )
        assert "special character" in str(exc_info.value)
    
    def test_password_too_long(self):
        """Test that password over 128 characters is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="A" * 129 + "a1!"
            )
        assert "128 characters" in str(exc_info.value)
    
    def test_valid_strong_password(self):
        """Test that strong password is accepted."""
        user = UserCreate(
            email="test@example.com",
            password="StrongP@ssw0rd!"
        )
        assert user.password == "StrongP@ssw0rd!"


class TestDataSizeValidation:
    """Test data size limits to prevent DoS attacks."""
    
    def test_task_input_data_too_large(self):
        """Test that input data over 100KB is rejected."""
        large_data = {"data": "x" * 100001}
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(
                title="Test Task",
                agent_type="finance",
                input_data=large_data
            )
        assert "exceeds maximum size" in str(exc_info.value)
    
    def test_task_result_data_too_large(self):
        """Test that result data over 500KB is rejected."""
        large_data = {"result": "x" * 500001}
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(
                title="Updated",
                result_data=large_data
            )
        assert "exceeds maximum size" in str(exc_info.value)
    
    def test_chat_message_metadata_too_large(self):
        """Test that metadata over 10KB is rejected."""
        large_metadata = {"data": "x" * 10001}
        with pytest.raises(ValidationError) as exc_info:
            ChatMessageCreate(
                session_id=1,
                agent_type="finance",
                role=MessageRole.USER,
                content="Test",
                metadata=large_metadata
            )
        assert "exceeds maximum size" in str(exc_info.value)
    
    def test_artifact_metadata_too_large(self):
        """Test that artifact metadata over 50KB is rejected."""
        large_metadata = {"data": "x" * 50001}
        with pytest.raises(ValidationError) as exc_info:
            ArtifactCreate(
                agent_type="finance",
                file_name="test.pdf",
                file_type="pdf",
                file_path="/storage/test.pdf",
                file_size=1024,
                metadata=large_metadata
            )
        assert "exceeds maximum size" in str(exc_info.value)


class TestInputSanitization:
    """Test that inputs are properly sanitized."""
    
    def test_task_title_whitespace_stripped(self):
        """Test that whitespace is stripped from task title."""
        task = TaskCreate(
            title="  Test Task  ",
            agent_type="finance"
        )
        assert task.title == "Test Task"
    
    def test_chat_message_content_whitespace_stripped(self):
        """Test that whitespace is stripped from message content."""
        message = ChatMessageCreate(
            session_id=1,
            agent_type="finance",
            role=MessageRole.USER,
            content="  Hello World  "
        )
        assert message.content == "Hello World"
    
    def test_artifact_file_name_whitespace_stripped(self):
        """Test that whitespace is stripped from file name."""
        artifact = ArtifactCreate(
            agent_type="finance",
            file_name="  test.pdf  ",
            file_type="pdf",
            file_path="/storage/test.pdf",
            file_size=1024
        )
        assert artifact.file_name == "test.pdf"
    
    def test_session_agent_name_whitespace_stripped(self):
        """Test that whitespace is stripped from agent name."""
        session = SessionCreate(
            agent_type="finance",
            agent_name="  Finance Agent  "
        )
        assert session.agent_name == "Finance Agent"


class TestRequiredFieldValidation:
    """Test that required fields are properly validated."""
    
    def test_task_update_requires_at_least_one_field(self):
        """Test that TaskUpdate requires at least one field."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate()
        assert "At least one field must be provided" in str(exc_info.value)
    
    def test_chat_message_empty_content_rejected(self):
        """Test that empty message content is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            ChatMessageCreate(
                session_id=1,
                agent_type="finance",
                role=MessageRole.USER,
                content="   "  # Only whitespace
            )
        assert "cannot be empty" in str(exc_info.value)
    
    def test_session_empty_agent_name_rejected(self):
        """Test that empty agent name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SessionCreate(
                agent_type="finance",
                agent_name="   "  # Only whitespace
            )
        assert "cannot be empty" in str(exc_info.value)
