from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ece16dee6db8"
down_revision = "604f500d0e91"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) items.current_qty (not null, default 0)
    op.add_column(
        "items",
        sa.Column("current_qty", sa.Integer(), nullable=False, server_default="0"),
    )

    # 2) counts.approved_count (nullable)
    op.add_column(
        "counts",
        sa.Column("approved_count", sa.Integer(), nullable=True),
    )

    # optional: drop the server default after backfilling existing rows
    op.alter_column("items", "current_qty", server_default=None)


def downgrade() -> None: 
    op.drop_column("counts", "approved_count")
    op.drop_column("items", "current_qty")
