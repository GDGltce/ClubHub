# Alembic migration for Media Gallery

from alembic import op
import sqlalchemy as sa
import app.models.mixins

# revision identifiers
revision = "b62baa9d710b"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "albums",
        sa.Column("club_id", app.models.mixins.UUID(), nullable=False),
        sa.Column("event_id", app.models.mixins.UUID(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("id", app.models.mixins.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["club_id"], ["clubs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "photos",
        sa.Column("album_id", app.models.mixins.UUID(), nullable=False),
        sa.Column("uploaded_by_id", app.models.mixins.UUID(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
        sa.Column("caption", sa.String(length=500), nullable=True),
        sa.Column("tag", sa.Enum(
            "BEFORE", "DURING", "AFTER", "POSTER", "GENERAL",
            name="phototag"
        ), nullable=False),
        sa.Column("is_cover", sa.Boolean(), nullable=False),
        sa.Column("id", app.models.mixins.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["album_id"], ["albums.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("photos")
    op.drop_table("albums")
