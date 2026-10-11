"""Add the club proposal needs-changes status."""
from alembic import op


revision = "20261011_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'clubstatus') THEN
                ALTER TYPE clubstatus ADD VALUE IF NOT EXISTS 'NEEDS_CHANGES';
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    pass
