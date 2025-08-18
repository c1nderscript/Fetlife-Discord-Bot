"""Add timed_messages table"""

from alembic import op
import sqlalchemy as sa

revision = "0006_add_timed_messages"
down_revision = "0005_add_audit_log"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "timed_messages",
        sa.Column("message_id", sa.BigInteger, primary_key=True),
        sa.Column("channel_id", sa.BigInteger, nullable=False),
        sa.Column("delete_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("timed_messages")
