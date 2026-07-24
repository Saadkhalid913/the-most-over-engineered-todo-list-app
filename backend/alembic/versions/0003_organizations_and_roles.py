"""add organizations, memberships, and scope todos by organization

Revision ID: 0003_organizations_and_roles
Revises: 0002_users_and_todo_owner
Create Date: 2026-07-24 06:30:00.000000

"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

revision: str = "0003_organizations_and_roles"
down_revision: str | Sequence[str] | None = "0002_users_and_todo_owner"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "organization_memberships",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_organization_memberships_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_organization_memberships_user_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_organization_memberships_org_user",
        ),
    )
    op.create_index(
        "ix_organization_memberships_organization_id",
        "organization_memberships",
        ["organization_id"],
    )
    op.create_index(
        "ix_organization_memberships_user_id",
        "organization_memberships",
        ["user_id"],
    )

    conn = op.get_bind()
    users = conn.execute(sa.text("SELECT id, username FROM users")).fetchall()
    personal_org_by_user: dict[str, str] = {}
    for user_id, username in users:
        org_id = str(uuid4())
        conn.execute(
            sa.text("INSERT INTO organizations (id, name) VALUES (:id, :name)"),
            {"id": org_id, "name": f"{username}'s workspace"},
        )
        conn.execute(
            sa.text(
                "INSERT INTO organization_memberships "
                "(id, organization_id, user_id, role) "
                "VALUES (:id, :organization_id, :user_id, :role)"
            ),
            {
                "id": str(uuid4()),
                "organization_id": org_id,
                "user_id": user_id,
                "role": "editor",
            },
        )
        personal_org_by_user[str(user_id)] = org_id

    op.add_column(
        "todos",
        sa.Column("organization_id", sa.String(length=36), nullable=True),
    )

    todos = conn.execute(sa.text("SELECT id, user_id FROM todos")).fetchall()
    for todo_id, user_id in todos:
        org_id = personal_org_by_user.get(str(user_id))
        if org_id is None:
            continue
        conn.execute(
            sa.text(
                "UPDATE todos SET organization_id = :organization_id WHERE id = :id"
            ),
            {"organization_id": org_id, "id": todo_id},
        )

    op.execute(sa.text("DELETE FROM todos WHERE organization_id IS NULL"))

    op.alter_column(
        "todos",
        "organization_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )
    op.create_foreign_key(
        "fk_todos_organization_id_organizations",
        "todos",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_todos_organization_id", "todos", ["organization_id"])


def downgrade() -> None:
    op.drop_index("ix_todos_organization_id", table_name="todos")
    op.drop_constraint(
        "fk_todos_organization_id_organizations",
        "todos",
        type_="foreignkey",
    )
    op.drop_column("todos", "organization_id")
    op.drop_index(
        "ix_organization_memberships_user_id",
        table_name="organization_memberships",
    )
    op.drop_index(
        "ix_organization_memberships_organization_id",
        table_name="organization_memberships",
    )
    op.drop_table("organization_memberships")
    op.drop_table("organizations")
