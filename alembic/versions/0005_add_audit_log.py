"""Add audit_log table"""

from alembic import op
import sqlalchemy as sa

revision = "0005_add_audit_log"
down_revision = "0004_add_lookup_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger, nullable=True),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("target", sa.String, nullable=True),
        sa.Column("details", sa.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
