from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "guilds",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "channels",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("guild_id", sa.BigInteger(), sa.ForeignKey("guilds.id"), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("settings_json", sa.JSON(), nullable=True),
    )
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("channel_id", sa.BigInteger(), sa.ForeignKey("channels.id"), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("target_id", sa.String(), nullable=False),
        sa.Column("target_kind", sa.String(), nullable=False),
        sa.Column("filters_json", sa.JSON(), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
    )
    op.create_table(
        "cursors",
        sa.Column("subscription_id", sa.Integer(), sa.ForeignKey("subscriptions.id"), primary_key=True),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column("last_item_ids_json", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "relay_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subscription_id", sa.Integer(), sa.ForeignKey("subscriptions.id"), nullable=False),
        sa.Column("item_id", sa.String(), nullable=False),
        sa.Column("item_hash", sa.String(), nullable=True),
        sa.Column("relayed_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nickname", sa.String(), nullable=False),
        sa.Column("fl_id", sa.String(), nullable=False, unique=True),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("fl_id", sa.String(), nullable=False, unique=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("region", sa.String(), nullable=True),
        sa.Column("start_at", sa.DateTime(), nullable=True),
        sa.Column("permalink", sa.String(), nullable=True),
        sa.Column("last_populated_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "rsvps",
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), primary_key=True),
        sa.Column("profile_fl_id", sa.String(), primary_key=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("seen_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("rsvps")
    op.drop_table("events")
    op.drop_table("profiles")
    op.drop_table("relay_log")
    op.drop_table("cursors")
    op.drop_table("subscriptions")
    op.drop_table("channels")
    op.drop_table("guilds")
