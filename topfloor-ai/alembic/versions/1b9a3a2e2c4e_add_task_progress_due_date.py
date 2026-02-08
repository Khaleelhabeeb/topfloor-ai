"""add_task_progress_due_date

Revision ID: 1b9a3a2e2c4e
Revises: e7a72975edcf
Create Date: 2026-02-07 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1b9a3a2e2c4e"
down_revision: Union[str, None] = "e7a72975edcf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0")
    )
    op.add_column(
        "tasks",
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("tasks", "due_date")
    op.drop_column("tasks", "progress")
