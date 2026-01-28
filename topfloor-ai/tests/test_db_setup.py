import pytest
from sqlalchemy import Column, Integer, String
from app.db.base import Base
from app.db.session import get_db, SessionLocal, engine


def test_base_class_exists():
    """Test that the Base declarative class is properly created."""
    assert Base is not None
    assert hasattr(Base, 'metadata')


def test_session_local_factory():
    """Test that SessionLocal creates valid database sessions."""
    db = SessionLocal()
    assert db is not None
    db.close()


def test_get_db_generator():
    """Test that get_db() provides a database session generator."""
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    
    # Clean up
    try:
        next(db_gen)
    except StopIteration:
        pass  # Expected behavior


def test_engine_configuration():
    """Test that the database engine is properly configured."""
    assert engine is not None
    assert engine.url is not None


def test_base_model_inheritance():
    """Test that models can inherit from Base properly."""
    
    class TestModel(Base):
        __tablename__ = "test_table"
        id = Column(Integer, primary_key=True)
        name = Column(String)
    
    # Verify the model has the expected attributes
    assert hasattr(TestModel, '__tablename__')
    assert TestModel.__tablename__ == "test_table"
    assert hasattr(TestModel, 'id')
    assert hasattr(TestModel, 'name')
