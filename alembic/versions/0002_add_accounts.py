"""Add accounts table and link subscriptions."""

from alembic import op
import sqlalchemy as sa

revision = "0002_add_accounts"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("credential_hash", sa.String(), nullable=False, unique=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    with op.batch_alter_table("subscriptions") as batch_op:
        batch_op.add_column(sa.Column("account_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_subscriptions_account_id_accounts",
            "accounts",
            ["account_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("subscriptions") as batch_op:
        batch_op.drop_constraint(
            "fk_subscriptions_account_id_accounts", type_="foreignkey"
        )
        batch_op.drop_column("account_id")
    op.drop_table("accounts")
