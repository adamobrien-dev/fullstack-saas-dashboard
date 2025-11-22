"""add password reset fields to users

Revision ID: 54509cdd52f4
Revises: 997f3d7cb37e
Create Date: 2025-11-21 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54509cdd52f4'
down_revision: Union[str, None] = '997f3d7cb37e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password reset fields to users table."""
    op.add_column('users', sa.Column('password_reset_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('password_reset_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index(op.f('ix_users_password_reset_token'), 'users', ['password_reset_token'], unique=False)


def downgrade() -> None:
    """Remove password reset fields from users table."""
    op.drop_index(op.f('ix_users_password_reset_token'), table_name='users')
    op.drop_column('users', 'password_reset_expires_at')
    op.drop_column('users', 'password_reset_token')
