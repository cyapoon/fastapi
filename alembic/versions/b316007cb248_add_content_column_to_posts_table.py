"""add content column to posts table

Revision ID: b316007cb248
Revises: 5e02e0da777d
Create Date: 2025-12-05 14:31:16.774136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b316007cb248'
down_revision: Union[str, Sequence[str], None] = '5e02e0da777d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'content')
    pass
