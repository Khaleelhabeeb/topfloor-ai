"""
Tests for Alembic database migrations.

This module tests that migrations can be applied (upgrade) and reverted (downgrade)
successfully without errors. These tests use a simpler approach that works with
the actual database state.
"""
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="module")
def alembic_config():
    """Create Alembic configuration."""
    config = Config("alembic.ini")
    return config


@pytest.fixture(scope="module")
def db_engine():
    """Create database engine for testing."""
    database_url = "postgresql://postgres.uhloeqddpdravorocpfm:Frelosystems13131.@aws-1-eu-central-2.pooler.supabase.com:6543/postgres"
    engine = create_engine(database_url)
    yield engine
    engine.dispose()


def test_current_migration_state(alembic_config):
    """Test that we can check the current migration state."""
    # This should not raise an error
    from alembic.script import ScriptDirectory
    script = ScriptDirectory.from_config(alembic_config)
    
    # Get all revisions
    revisions = list(script.walk_revisions())
    assert len(revisions) > 0, "No migrations found"
    
    # Verify we have the expected migrations
    revision_ids = [rev.revision for rev in revisions]
    assert 'bcf3c9272f9d' in revision_ids  # users table
    assert '4ff9d7947698' in revision_ids  # sessions table
    assert 'c8a47b806ab7' in revision_ids  # new models tables
    assert 'e7a72975edcf' in revision_ids  # performance indexes


def test_upgrade_to_head(alembic_config, db_engine):
    """Test upgrading to the latest migration."""
    # Upgrade to head
    command.upgrade(alembic_config, "head")
    
    # Verify we're at head
    with db_engine.connect() as conn:
        result = conn.execute(
            text("SELECT version_num FROM alembic_version")
        )
        current_version = result.scalar()
        assert current_version == 'e7a72975edcf', f"Expected e7a72975edcf, got {current_version}"


def test_all_tables_exist(db_engine):
    """Test that all expected tables exist after migration to head."""
    inspector = inspect(db_engine)
    tables = inspector.get_table_names()
    
    expected_tables = [
        "users",
        "sessions",
        "tasks",
        "task_history",
        "chat_messages",
        "agent_status"
    ]
    
    for table in expected_tables:
        assert table in tables, f"Table {table} not found"


def test_users_table_structure(db_engine):
    """Test that users table has correct structure."""
    inspector = inspect(db_engine)
    columns = {col["name"]: col for col in inspector.get_columns("users")}
    
    # Check required columns exist
    required_columns = ["id", "email", "password_hash", "created_at", "updated_at"]
    for col in required_columns:
        assert col in columns, f"Column {col} not found in users table"
    
    # Check indexes
    indexes = inspector.get_indexes("users")
    index_names = [idx["name"] for idx in indexes]
    assert "ix_users_email" in index_names
    assert "ix_users_id" in index_names


def test_sessions_table_structure(db_engine):
    """Test that sessions table has correct structure."""
    inspector = inspect(db_engine)
    columns = {col["name"]: col for col in inspector.get_columns("sessions")}
    
    # Check required columns exist
    required_columns = ["id", "session_id", "user_id", "agent_type", "agent_name", "status"]
    for col in required_columns:
        assert col in columns, f"Column {col} not found in sessions table"
    
    # Check foreign keys
    foreign_keys = inspector.get_foreign_keys("sessions")
    assert len(foreign_keys) > 0
    assert any(fk["referred_table"] == "users" for fk in foreign_keys)


def test_tasks_table_structure(db_engine):
    """Test that tasks table has correct structure."""
    inspector = inspect(db_engine)
    columns = {col["name"]: col for col in inspector.get_columns("tasks")}
    
    # Check required columns exist
    required_columns = ["id", "task_id", "user_id", "agent_type", "title", "task_type", "priority", "status"]
    for col in required_columns:
        assert col in columns, f"Column {col} not found in tasks table"
    
    # Check foreign keys
    foreign_keys = inspector.get_foreign_keys("tasks")
    assert any(fk["referred_table"] == "users" for fk in foreign_keys)


def test_referential_integrity(db_engine):
    """Test that foreign key relationships are properly set up."""
    inspector = inspect(db_engine)
    
    # Check chat_messages references sessions and users
    chat_fks = inspector.get_foreign_keys("chat_messages")
    referred_tables = [fk["referred_table"] for fk in chat_fks]
    assert "sessions" in referred_tables
    assert "users" in referred_tables
    
    # Check task_history references tasks
    task_history_fks = inspector.get_foreign_keys("task_history")
    referred_tables = [fk["referred_table"] for fk in task_history_fks]
    assert "tasks" in referred_tables
    
    # Check agent_status references users and tasks
    agent_status_fks = inspector.get_foreign_keys("agent_status")
    referred_tables = [fk["referred_table"] for fk in agent_status_fks]
    assert "users" in referred_tables
    assert "tasks" in referred_tables


def test_downgrade_one_step(alembic_config, db_engine):
    """Test downgrading one migration step."""
    # Downgrade from c8a47b806ab7 to 4ff9d7947698
    command.downgrade(alembic_config, "4ff9d7947698")
    
    # Verify we're at the correct version
    with db_engine.connect() as conn:
        result = conn.execute(
            text("SELECT version_num FROM alembic_version")
        )
        current_version = result.scalar()
        assert current_version == '4ff9d7947698'
    
    # Verify tables from the latest migration are gone
    inspector = inspect(db_engine)
    tables = inspector.get_table_names()
    
    # These tables should not exist after downgrade
    assert "tasks" not in tables
    assert "task_history" not in tables
    assert "chat_messages" not in tables
    assert "agent_status" not in tables
    
    # These tables should still exist
    assert "users" in tables
    assert "sessions" in tables


def test_upgrade_back_to_head(alembic_config, db_engine):
    """Test upgrading back to head after downgrade."""
    # Upgrade back to head
    command.upgrade(alembic_config, "head")
    
    # Verify we're at head
    with db_engine.connect() as conn:
        result = conn.execute(
            text("SELECT version_num FROM alembic_version")
        )
        current_version = result.scalar()
        assert current_version == 'e7a72975edcf'
    
    # Verify all tables exist again
    inspector = inspect(db_engine)
    tables = inspector.get_table_names()
    
    expected_tables = [
        "users",
        "sessions",
        "tasks",
        "task_history",
        "chat_messages",
        "agent_status"
    ]
    
    for table in expected_tables:
        assert table in tables, f"Table {table} not found after upgrade"
