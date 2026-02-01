import pytest
from sqlalchemy import inspect
from app.models.artifact import Artifact
from app.db.base import Base


def test_artifact_model_exists():
    """Test that the Artifact model is properly defined."""
    assert Artifact is not None
    assert hasattr(Artifact, '__tablename__')
    assert Artifact.__tablename__ == "artifacts"


def test_artifact_model_inherits_from_base():
    """Test that Artifact model inherits from Base."""
    assert issubclass(Artifact, Base)


def test_artifact_model_has_required_columns():
    """Test that Artifact model has all required columns."""
    columns = {col.name for col in Artifact.__table__.columns}
    required_columns = {
        'id', 'artifact_id', 'task_id', 'user_id', 'agent_type',
        'file_name', 'file_type', 'file_path', 'file_size', 
        'mime_type', 'meta_data', 'created_at'
    }
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"


def test_artifact_id_is_primary_key():
    """Test that id column is the primary key."""
    id_col = Artifact.__table__.columns['id']
    assert id_col.primary_key is True
    assert id_col.nullable is False


def test_artifact_artifact_id_is_unique_and_indexed():
    """Test that artifact_id column is unique and indexed."""
    artifact_id_col = Artifact.__table__.columns['artifact_id']
    assert artifact_id_col.unique is True
    assert artifact_id_col.index is True
    assert artifact_id_col.nullable is False


def test_artifact_user_id_is_not_nullable():
    """Test that user_id column is not nullable."""
    user_id_col = Artifact.__table__.columns['user_id']
    assert user_id_col.nullable is False


def test_artifact_task_id_is_nullable():
    """Test that task_id column is nullable (optional association)."""
    task_id_col = Artifact.__table__.columns['task_id']
    assert task_id_col.nullable is True


def test_artifact_file_info_columns_not_nullable():
    """Test that file information columns are not nullable."""
    file_name_col = Artifact.__table__.columns['file_name']
    file_type_col = Artifact.__table__.columns['file_type']
    file_path_col = Artifact.__table__.columns['file_path']
    file_size_col = Artifact.__table__.columns['file_size']
    
    assert file_name_col.nullable is False
    assert file_type_col.nullable is False
    assert file_path_col.nullable is False
    assert file_size_col.nullable is False


def test_artifact_mime_type_is_nullable():
    """Test that mime_type column is nullable."""
    mime_type_col = Artifact.__table__.columns['mime_type']
    assert mime_type_col.nullable is True


def test_artifact_meta_data_is_nullable():
    """Test that meta_data column is nullable."""
    meta_data_col = Artifact.__table__.columns['meta_data']
    assert meta_data_col.nullable is True


def test_artifact_created_at_has_default():
    """Test that created_at has a default value."""
    created_at_col = Artifact.__table__.columns['created_at']
    assert created_at_col.default is not None


def test_artifact_has_foreign_keys():
    """Test that Artifact has foreign key relationships."""
    foreign_keys = {fk.parent.name: fk.column.table.name for fk in Artifact.__table__.foreign_keys}
    assert 'user_id' in foreign_keys
    assert foreign_keys['user_id'] == 'users'
    assert 'task_id' in foreign_keys
    assert foreign_keys['task_id'] == 'tasks'


def test_artifact_indexes_exist():
    """Test that indexes exist on key columns."""
    indexed_columns = {col.name for col in Artifact.__table__.columns if col.index}
    expected_indexes = {'artifact_id', 'task_id', 'user_id', 'agent_type'}
    assert expected_indexes.issubset(indexed_columns), f"Missing indexes: {expected_indexes - indexed_columns}"


def test_artifact_to_dict_method():
    """Test that Artifact has a to_dict method."""
    assert hasattr(Artifact, 'to_dict')
    assert callable(getattr(Artifact, 'to_dict'))


def test_artifact_repr_method():
    """Test that Artifact has a __repr__ method."""
    assert hasattr(Artifact, '__repr__')
    assert callable(getattr(Artifact, '__repr__'))
