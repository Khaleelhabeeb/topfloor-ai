import pytest
from sqlalchemy import inspect
from app.models.task_history import TaskHistory
from app.db.base import Base


def test_task_history_model_exists():
    """Test that the TaskHistory model is properly defined."""
    assert TaskHistory is not None
    assert hasattr(TaskHistory, '__tablename__')
    assert TaskHistory.__tablename__ == "task_history"


def test_task_history_model_inherits_from_base():
    """Test that TaskHistory model inherits from Base."""
    assert issubclass(TaskHistory, Base)


def test_task_history_model_has_required_columns():
    """Test that TaskHistory model has all required columns."""
    columns = {col.name for col in TaskHistory.__table__.columns}
    required_columns = {'id', 'task_id', 'status', 'message', 'metadata', 'created_at'}
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"


def test_task_history_id_is_primary_key():
    """Test that id column is the primary key."""
    id_col = TaskHistory.__table__.columns['id']
    assert id_col.primary_key is True
    assert id_col.nullable is False


def test_task_history_task_id_is_foreign_key():
    """Test that task_id column is a foreign key."""
    task_id_col = TaskHistory.__table__.columns['task_id']
    assert task_id_col.nullable is False
    assert task_id_col.index is True
    
    # Check foreign key constraint
    foreign_keys = list(task_id_col.foreign_keys)
    assert len(foreign_keys) > 0, "task_id should have a foreign key constraint"
    assert foreign_keys[0].column.table.name == "tasks"


def test_task_history_status_is_not_nullable():
    """Test that status column is not nullable."""
    status_col = TaskHistory.__table__.columns['status']
    assert status_col.nullable is False


def test_task_history_message_is_nullable():
    """Test that message column is nullable."""
    message_col = TaskHistory.__table__.columns['message']
    assert message_col.nullable is True


def test_task_history_metadata_is_nullable():
    """Test that metadata column is nullable."""
    # Note: The column is named 'metadata' in the database but accessed as 'event_metadata' in Python
    metadata_col = TaskHistory.__table__.columns['metadata']
    assert metadata_col.nullable is True


def test_task_history_created_at_exists():
    """Test that created_at column exists."""
    created_at_col = TaskHistory.__table__.columns['created_at']
    assert created_at_col is not None
    assert created_at_col.nullable is False


def test_task_history_created_at_has_default():
    """Test that created_at has a default value."""
    created_at_col = TaskHistory.__table__.columns['created_at']
    assert created_at_col.default is not None


def test_task_history_task_id_index_exists():
    """Test that an index exists on the task_id column."""
    task_id_col = TaskHistory.__table__.columns['task_id']
    assert task_id_col.index is True


def test_task_history_has_relationship_to_task():
    """Test that TaskHistory has a relationship to Task."""
    assert hasattr(TaskHistory, 'task')


def test_task_history_to_dict_method():
    """Test that TaskHistory has a to_dict method."""
    assert hasattr(TaskHistory, 'to_dict')
    assert callable(TaskHistory.to_dict)
