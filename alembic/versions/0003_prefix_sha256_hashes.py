"""Prefix existing SHA-256 credential hashes"""

from alembic import op

revision = "0003_prefix_sha256_hashes"
down_revision = "0002_add_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE accounts SET credential_hash = 'sha256$' || credential_hash")


def downgrade() -> None:
    op.execute(
        "UPDATE accounts SET credential_hash = substr(credential_hash, 8) "
        "WHERE credential_hash LIKE 'sha256$%'"
    )
