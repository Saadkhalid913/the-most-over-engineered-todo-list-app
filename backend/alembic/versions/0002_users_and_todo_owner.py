"""add users and scope todos by user_id

Revision ID: 0002_users_and_todo_owner
Revises: 0001_create_todos
Create Date: 2026-07-24 02:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_users_and_todo_owner"
down_revision: str | Sequence[str] | None = "0001_create_todos"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    # Existing todos have no owner; clear them before requiring user_id.
    op.execute(sa.text("DELETE FROM todos"))

    op.add_column("todos", sa.Column("user_id", sa.String(length=36), nullable=False))
    op.create_foreign_key(
        "fk_todos_user_id_users",
        "todos",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_todos_user_id", "todos", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_todos_user_id", table_name="todos")
    op.drop_constraint("fk_todos_user_id_users", "todos", type_="foreignkey")
    op.drop_column("todos", "user_id")
    op.drop_table("users")
