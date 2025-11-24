"""add_avatar_url_to_users

Revision ID: 2afc300d95c6
Revises: 54509cdd52f4
Create Date: 2025-11-23 20:35:25.604556

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2afc300d95c6'
down_revision: Union[str, Sequence[str], None] = '54509cdd52f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('avatar_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'avatar_url')
