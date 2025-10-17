"""fix: add items.current_qty and counts.approved_count

Revision ID: 3a014ed63d93
Revises: 5b4e5d75bb0e
Create Date: 2025-10-17 15:43:35.877780

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "3a014ed63d93"
down_revision = "5b4e5d75bb0e"   # <-- keep this; it comes after your enum migration
branch_labels = None
depends_on = None

def upgrade():
    # Add items.current_qty if missing
    op.add_column(
        "items",
        sa.Column("current_qty", sa.Integer(), nullable=False, server_default="0"),
    )

    # Add counts.approved_count if missing
    op.add_column(
        "counts",
        sa.Column("approved_count", sa.Integer(), nullable=True),
    )

    # Drop server_default so future inserts use ORM default
    op.alter_column("items", "current_qty", server_default=None)

def downgrade():
    op.drop_column("counts", "approved_count")
    op.drop_column("items", "current_qty")
