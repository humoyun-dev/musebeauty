"""product gallery

Revision ID: c7d4e9a1b2f3
Revises: b99a26875a4d
Create Date: 2026-06-17 01:50:00.000000+05:00
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7d4e9a1b2f3'
down_revision: str | None = 'b99a26875a4d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # products.gallery — mahsulot rasmlari ro'yxati (JSON). Eski qatorlar [] bilan
    # to'ldiriladi; ular Product.images orqali image_url ga fallback qiladi.
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('gallery', sa.JSON(), nullable=False, server_default=sa.text("'[]'"))
        )


def downgrade() -> None:
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('gallery')
