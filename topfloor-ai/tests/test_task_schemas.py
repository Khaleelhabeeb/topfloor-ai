"""
Tests for Task Schemas
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas.task import (
    TaskType,
    TaskStatus,
    TaskPriority,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)


class TestTaskCreate:
    """Tests for TaskCreate schema."""
    
    def test_valid_task_create_minimal(self):
        """Test that valid minimal task creation data is accepted."""
        task = TaskCreate(
            title="Test Task",
            agent_type="finance"
        )
        assert task.title == "Test Task"
        assert task.agent_type == "finance"
        assert task.task_type == TaskType.BACKGROUND
        assert task.priority == TaskPriority.MEDIUM
        assert task.description is None
        assert task.input_data is None
    
    def test_valid_task_create_full(self):
        """Test that valid full task creation data is accepted."""
        task = TaskCreate(
            title="Analyze Portfolio",
            description="Analyze my investment portfolio",
            agent_type="finance",
            task_type=TaskType.CHAT,
            priority=TaskPriority.HIGH,
            input_data={"portfolio_id": 123}
        )
        assert task.title == "Analyze Portfolio"
        assert task.description == "Analyze my investment portfolio"
        assert task.agent_type == "finance"
        assert task.task_type == TaskType.CHAT
        assert task.priority == TaskPriority.HIGH
        assert task.input_data == {"portfolio_id": 123}
    
    def test_missing_title(self):
        """Test that missing title is rejected."""
        with pytest.raises(ValidationError):
            TaskCreate(agent_type="finance")
    
    def test_missing_agent_type(self):
        """Test that missing agent_type is rejected."""
        with pytest.raises(ValidationError):
            TaskCreate(title="Test Task")
    
    def test_empty_title(self):
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError):
            TaskCreate(title="", agent_type="finance")
    
    def test_title_too_long(self):
        """Test that title longer than 255 characters is rejected."""
        with pytest.raises(ValidationError):
            TaskCreate(title="x" * 256, agent_type="finance")
    
    def test_title_exactly_255_characters(self):
        """Test that title with exactly 255 characters is accepted."""
        task = TaskCreate(title="x" * 255, agent_type="finance")
        assert len(task.title) == 255
    
    def test_default_task_type(self):
        """Test that task_type defaults to BACKGROUND."""
        task = TaskCreate(title="Test", agent_type="finance")
        assert task.task_type == TaskType.BACKGROUND
    
    def test_default_priority(self):
        """Test that priority defaults to MEDIUM."""
        task = TaskCreate(title="Test", agent_type="finance")
        assert task.priority == TaskPriority.MEDIUM
    
    def test_all_task_types(self):
        """Test that all task types are accepted."""
        for task_type in TaskType:
            task = TaskCreate(
                title="Test",
                agent_type="finance",
                task_type=task_type
            )
            assert task.task_type == task_type
    
    def test_all_priorities(self):
        """Test that all priority levels are accepted."""
        for priority in TaskPriority:
            task = TaskCreate(
                title="Test",
                agent_type="finance",
                priority=priority
            )
            assert task.priority == priority
    
    def test_input_data_dict(self):
        """Test that input_data accepts dictionary."""
        task = TaskCreate(
            title="Test",
            agent_type="finance",
            input_data={"key": "value", "nested": {"data": 123}}
        )
        assert task.input_data == {"key": "value", "nested": {"data": 123}}


class TestTaskUpdate:
    """Tests for TaskUpdate schema."""
    
    def test_valid_task_update_all_fields(self):
        """Test that all fields can be updated."""
        update = TaskUpdate(
            title="Updated Title",
            description="Updated description",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.HIGH,
            result_data={"result": "success"},
            error_message="No errors"
        )
        assert update.title == "Updated Title"
        assert update.description == "Updated description"
        assert update.status == TaskStatus.COMPLETED
        assert update.priority == TaskPriority.HIGH
        assert update.result_data == {"result": "success"}
        assert update.error_message == "No errors"
    
    def test_valid_task_update_partial(self):
        """Test that partial updates are accepted."""
        update = TaskUpdate(status=TaskStatus.IN_PROGRESS)
        assert update.status == TaskStatus.IN_PROGRESS
        assert update.title is None
        assert update.description is None
        assert update.priority is None
    
    def test_empty_task_update(self):
        """Test that empty update is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate()
        
        assert "At least one field must be provided for update" in str(exc_info.value)
    
    def test_title_too_long(self):
        """Test that title longer than 255 characters is rejected."""
        with pytest.raises(ValidationError):
            TaskUpdate(title="x" * 256)
    
    def test_all_statuses(self):
        """Test that all status values are accepted."""
        for status in TaskStatus:
            update = TaskUpdate(status=status)
            assert update.status == status
    
    def test_result_data_dict(self):
        """Test that result_data accepts dictionary."""
        update = TaskUpdate(
            result_data={"output": "data", "metrics": {"count": 10}}
        )
        assert update.result_data == {"output": "data", "metrics": {"count": 10}}


class TestTaskResponse:
    """Tests for TaskResponse schema."""
    
    def test_valid_task_response_minimal(self):
        """Test that valid minimal task response is accepted."""
        task = TaskResponse(
            id=1,
            task_id="task_123",
            user_id=1,
            title="Test Task",
            description=None,
            agent_type="finance",
            task_type=TaskType.BACKGROUND,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            input_data=None,
            result_data=None,
            error_message=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            started_at=None,
            completed_at=None
        )
        assert task.id == 1
        assert task.task_id == "task_123"
        assert task.user_id == 1
        assert task.title == "Test Task"
        assert task.agent_type == "finance"
        assert task.status == TaskStatus.PENDING
    
    def test_valid_task_response_full(self):
        """Test that valid full task response is accepted."""
        now = datetime.now()
        task = TaskResponse(
            id=1,
            task_id="task_123",
            user_id=1,
            title="Test Task",
            description="Task description",
            agent_type="finance",
            task_type=TaskType.CHAT,
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.HIGH,
            input_data={"input": "data"},
            result_data={"output": "result"},
            error_message=None,
            created_at=now,
            updated_at=now,
            started_at=now,
            completed_at=now
        )
        assert task.description == "Task description"
        assert task.task_type == TaskType.CHAT
        assert task.input_data == {"input": "data"}
        assert task.result_data == {"output": "result"}
        assert task.started_at == now
        assert task.completed_at == now
    
    def test_missing_required_fields(self):
        """Test that missing required fields are rejected."""
        with pytest.raises(ValidationError):
            TaskResponse(
                id=1,
                title="Test"
            )
    
    def test_from_attributes_config(self):
        """Test that from_attributes is enabled for SQLAlchemy model conversion."""
        assert TaskResponse.model_config.get('from_attributes') is True


class TestTaskListResponse:
    """Tests for TaskListResponse schema."""
    
    def test_valid_task_list_response(self):
        """Test that valid task list response is accepted."""
        now = datetime.now()
        task1 = TaskResponse(
            id=1,
            task_id="task_1",
            user_id=1,
            title="Task 1",
            description=None,
            agent_type="finance",
            task_type=TaskType.BACKGROUND,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            input_data=None,
            result_data=None,
            error_message=None,
            created_at=now,
            updated_at=now,
            started_at=None,
            completed_at=None
        )
        
        task_list = TaskListResponse(
            tasks=[task1],
            total=1,
            page=1,
            page_size=10
        )
        assert len(task_list.tasks) == 1
        assert task_list.total == 1
        assert task_list.page == 1
        assert task_list.page_size == 10
    
    def test_empty_task_list(self):
        """Test that empty task list is accepted."""
        task_list = TaskListResponse(
            tasks=[],
            total=0,
            page=1,
            page_size=10
        )
        assert len(task_list.tasks) == 0
        assert task_list.total == 0


class TestTaskEnums:
    """Tests for Task enumeration types."""
    
    def test_task_type_values(self):
        """Test that TaskType has correct values."""
        assert TaskType.CHAT.value == "chat"
        assert TaskType.BACKGROUND.value == "background"
    
    def test_task_status_values(self):
        """Test that TaskStatus has correct values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.QUEUED.value == "queued"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
    
    def test_task_priority_values(self):
        """Test that TaskPriority has correct values."""
        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.CRITICAL.value == "critical"
