"""Add welcome_configs table"""

from alembic import op
import sqlalchemy as sa

revision = "0007_add_welcome_configs"
down_revision = "0006_add_timed_messages"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "welcome_configs",
        sa.Column("guild_id", sa.BigInteger, primary_key=True),
        sa.Column("channel_id", sa.BigInteger, nullable=False),
        sa.Column("message", sa.String, nullable=False),
        sa.Column("verify_role_id", sa.BigInteger, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("welcome_configs")
