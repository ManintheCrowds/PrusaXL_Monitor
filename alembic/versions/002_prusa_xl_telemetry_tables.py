"""Add Prusa XL diagnostics tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-15 00:00:00.000000
"""

# PURPOSE: Alembic migration for Prusa XL diagnostics tables.
# DEPENDENCIES: alembic.op, sqlalchemy, sqlalchemy.dialects.postgresql
# MODIFICATION NOTES: v0.1 - Add error events and telemetry sample tables.

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


# PURPOSE: Create Prusa XL diagnostics tables and indexes.
# DEPENDENCIES: alembic.op, sqlalchemy
# MODIFICATION NOTES: v0.1 - Add event and telemetry tables.
def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    json_type = postgresql.JSONB if dialect == "postgresql" else sa.JSON

    op.create_table(
        "prusa_xl_error_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("printer_id", sa.String(64), nullable=False),
        sa.Column("error_code", sa.String(64), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False, server_default="unknown"),
        sa.Column("subsystem", sa.String(64)),
        sa.Column("event_time", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("raw_payload", json_type),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("idx_prusa_xl_error_events_printer", "prusa_xl_error_events", ["printer_id"])
    op.create_index("idx_prusa_xl_error_events_code", "prusa_xl_error_events", ["error_code"])
    op.create_index("idx_prusa_xl_error_events_time", "prusa_xl_error_events", ["event_time"])

    op.create_table(
        "prusa_xl_telemetry_samples",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("printer_id", sa.String(64), nullable=False),
        sa.Column("sample_time", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("nozzle_temp_c", sa.Float()),
        sa.Column("bed_temp_c", sa.Float()),
        sa.Column("chamber_temp_c", sa.Float()),
        sa.Column("fan_speed_pct", sa.Float()),
        sa.Column("print_progress_pct", sa.Float()),
        sa.Column("print_state", sa.String(64)),
        sa.Column("toolhead_id", sa.String(64)),
        sa.Column("job_id", sa.String(128)),
        sa.Column("raw_payload", json_type),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("idx_prusa_xl_telemetry_printer", "prusa_xl_telemetry_samples", ["printer_id"])
    op.create_index("idx_prusa_xl_telemetry_time", "prusa_xl_telemetry_samples", ["sample_time"])


# PURPOSE: Drop Prusa XL diagnostics tables and indexes.
# DEPENDENCIES: alembic.op
# MODIFICATION NOTES: v0.1 - Remove event and telemetry tables.
def downgrade() -> None:
    op.drop_index("idx_prusa_xl_telemetry_time", "prusa_xl_telemetry_samples")
    op.drop_index("idx_prusa_xl_telemetry_printer", "prusa_xl_telemetry_samples")
    op.drop_table("prusa_xl_telemetry_samples")

    op.drop_index("idx_prusa_xl_error_events_time", "prusa_xl_error_events")
    op.drop_index("idx_prusa_xl_error_events_code", "prusa_xl_error_events")
    op.drop_index("idx_prusa_xl_error_events_printer", "prusa_xl_error_events")
    op.drop_table("prusa_xl_error_events")
