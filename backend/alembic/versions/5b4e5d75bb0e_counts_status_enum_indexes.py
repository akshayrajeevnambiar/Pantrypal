"""counts.status enum + indexes

Revision ID: 5b4e5d75bb0e
Revises: ece16dee6db8
Create Date: 2025-10-17 15:13:33.783838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b4e5d75bb0e'
down_revision: Union[str, Sequence[str], None] = 'ece16dee6db8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # --- 1) Create the enum type (PostgreSQL) ---
    op.execute("CREATE TYPE count_status AS ENUM ('pending','approved','rejected')")

    # --- 2) Alter the column to use enum ---
    # Using raw SQL for safety across versions
    op.execute("""
        ALTER TABLE counts
        ALTER COLUMN status DROP DEFAULT,
        ALTER COLUMN status TYPE count_status USING status::count_status,
        ALTER COLUMN status SET DEFAULT 'pending',
        ALTER COLUMN status SET NOT NULL
    """)

    # --- 3) Indexes for common filters ---
    op.create_index("ix_counts_status", "counts", ["status"])
    op.create_index("ix_counts_item_id", "counts", ["item_id"])
    op.create_index("ix_counts_submitted_by", "counts", ["submitted_by"])


def downgrade():
    # Drop indexes first
    op.drop_index("ix_counts_submitted_by", table_name="counts")
    op.drop_index("ix_counts_item_id", table_name="counts")
    op.drop_index("ix_counts_status", table_name="counts")

    # Convert enum back to string (varchar)
    op.execute("""
        ALTER TABLE counts
        ALTER COLUMN status DROP DEFAULT,
        ALTER COLUMN status TYPE VARCHAR(20),
        ALTER COLUMN status SET DEFAULT 'pending',
        ALTER COLUMN status SET NOT NULL
    """)

    # Finally drop the enum type
    op.execute("DROP TYPE count_status")
