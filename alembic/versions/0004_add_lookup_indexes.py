"""Add indexes for frequent lookups"""

from alembic import op
import sqlalchemy as sa

revision = "0004_add_lookup_indexes"
down_revision = "0003_prefix_sha256_hashes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_subscriptions_channel_id", "subscriptions", ["channel_id"])
    op.create_index("ix_relay_log_subscription_id", "relay_log", ["subscription_id"])
    op.create_index("ix_relay_log_item_id", "relay_log", ["item_id"])


def downgrade() -> None:
    op.drop_index("ix_relay_log_item_id", table_name="relay_log")
    op.drop_index("ix_relay_log_subscription_id", table_name="relay_log")
    op.drop_index("ix_subscriptions_channel_id", table_name="subscriptions")
