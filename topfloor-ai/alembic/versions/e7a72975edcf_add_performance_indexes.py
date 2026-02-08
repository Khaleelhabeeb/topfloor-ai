"""add_performance_indexes

Revision ID: e7a72975edcf
Revises: c8a47b806ab7
Create Date: 2026-02-01 14:39:23.503239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7a72975edcf'
down_revision: Union[str, None] = 'c8a47b806ab7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add composite indexes for Tasks table
    op.create_index('idx_task_user_agent', 'tasks', ['user_id', 'agent_type'], unique=False)
    op.create_index('idx_task_user_agent_status', 'tasks', ['user_id', 'agent_type', 'status'], unique=False)
    op.create_index('idx_task_status_priority', 'tasks', ['status', 'priority'], unique=False)
    op.create_index('idx_task_agent_status', 'tasks', ['agent_type', 'status'], unique=False)
    op.create_index('idx_task_created_at', 'tasks', ['created_at'], unique=False)
    
    # Add composite indexes for TaskHistory table
    op.create_index('idx_task_history_task_created', 'task_history', ['task_id', 'created_at'], unique=False)
    
    # Add composite indexes for AgentStatus table
    op.create_index('idx_agent_status_user', 'agent_status', ['user_id'], unique=False)
    op.create_index('idx_agent_status_status', 'agent_status', ['status'], unique=False)
    
    # Add composite indexes for Sessions table
    op.create_index('idx_session_user_agent', 'sessions', ['user_id', 'agent_type'], unique=False)
    op.create_index('idx_session_user_status', 'sessions', ['user_id', 'status'], unique=False)
    op.create_index('idx_session_created_at', 'sessions', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop indexes in reverse order
    # Sessions indexes
    op.drop_index('idx_session_created_at', table_name='sessions')
    op.drop_index('idx_session_user_status', table_name='sessions')
    op.drop_index('idx_session_user_agent', table_name='sessions')
    
    # AgentStatus indexes
    op.drop_index('idx_agent_status_status', table_name='agent_status')
    op.drop_index('idx_agent_status_user', table_name='agent_status')
    
    # TaskHistory indexes
    op.drop_index('idx_task_history_task_created', table_name='task_history')
    
    # Tasks indexes
    op.drop_index('idx_task_created_at', table_name='tasks')
    op.drop_index('idx_task_agent_status', table_name='tasks')
    op.drop_index('idx_task_status_priority', table_name='tasks')
    op.drop_index('idx_task_user_agent_status', table_name='tasks')
    op.drop_index('idx_task_user_agent', table_name='tasks')
