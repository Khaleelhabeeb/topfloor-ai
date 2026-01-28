import pytest
from sqlalchemy import inspect
from app.models.user import User
from app.db.base import Base


def test_user_model_exists():
    """Test that the User model is properly defined."""
    assert User is not None
    assert hasattr(User, '__tablename__')
    assert User.__tablename__ == "users"


def test_user_model_inherits_from_base():
    """Test that User model inherits from Base."""
    assert issubclass(User, Base)


def test_user_model_has_required_columns():
    """Test that User model has all required columns."""
    columns = {col.name for col in User.__table__.columns}
    required_columns = {'id', 'email', 'password_hash', 'created_at', 'updated_at'}
    assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"


def test_user_id_is_primary_key():
    """Test that id column is the primary key."""
    id_col = User.__table__.columns['id']
    assert id_col.primary_key is True
    assert id_col.nullable is False


def test_user_email_is_unique_and_indexed():
    """Test that email column is unique and indexed."""
    email_col = User.__table__.columns['email']
    assert email_col.unique is True
    assert email_col.index is True
    assert email_col.nullable is False


def test_user_password_hash_is_not_nullable():
    """Test that password_hash column is not nullable."""
    password_hash_col = User.__table__.columns['password_hash']
    assert password_hash_col.nullable is False


def test_user_timestamps_exist():
    """Test that created_at and updated_at columns exist."""
    created_at_col = User.__table__.columns['created_at']
    updated_at_col = User.__table__.columns['updated_at']
    
    assert created_at_col is not None
    assert updated_at_col is not None


def test_user_created_at_has_server_default():
    """Test that created_at has a server default value."""
    created_at_col = User.__table__.columns['created_at']
    assert created_at_col.server_default is not None


def test_user_updated_at_has_onupdate():
    """Test that updated_at has onupdate configured."""
    updated_at_col = User.__table__.columns['updated_at']
    assert updated_at_col.onupdate is not None


def test_user_email_index_exists():
    """Test that an index exists on the email column."""
    indexes = {idx.name for idx in User.__table__.indexes}
    # Check that there's an index containing 'email'
    email_indexes = [idx for idx in User.__table__.indexes if 'email' in [c.name for c in idx.columns]]
    assert len(email_indexes) > 0, "No index found on email column"
