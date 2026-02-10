"""Add knowledge base entries table

Revision ID: 003
Revises: 002
Create Date: 2026-01-15 00:00:00.000000
"""

# PURPOSE: Alembic migration for KB entries table.
# DEPENDENCIES: alembic.op, sqlalchemy
# MODIFICATION NOTES: v0.1 - Add kb_entries table.

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


# PURPOSE: Create KB entries table.
# DEPENDENCIES: alembic.op, sqlalchemy
# MODIFICATION NOTES: v0.1 - Add KB entries table and indexes.
def upgrade() -> None:
    op.create_table(
        "kb_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("url", sa.String(512)),
        sa.Column("error_code", sa.String(64)),
        sa.Column("symptoms", sa.String(255)),
        sa.Column("guidance", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    op.create_index("idx_kb_entries_error_code", "kb_entries", ["error_code"])
    op.create_index("idx_kb_entries_source", "kb_entries", ["source"])


# PURPOSE: Drop KB entries table.
# DEPENDENCIES: alembic.op
# MODIFICATION NOTES: v0.1 - Remove KB entries table and indexes.
def downgrade() -> None:
    op.drop_index("idx_kb_entries_source", "kb_entries")
    op.drop_index("idx_kb_entries_error_code", "kb_entries")
    op.drop_table("kb_entries")
