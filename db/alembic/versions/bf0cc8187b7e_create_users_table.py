# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create users table

Revision ID: bf0cc8187b7e
Revises:
Create Date: 2017-08-14 21:35:09.539979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf0cc8187b7e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('password', sa.String(44), nullable=False),
        sa.Column('firstname', sa.String(50), nullable=False)
    )


def downgrade():
    op.drop_table('users')
