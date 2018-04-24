# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add active column to users table

Revision ID: 1cfbd0896037
Revises: f779f40a2452
Create Date: 2017-08-23 15:57:35.239216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1cfbd0896037'
down_revision = 'f779f40a2452'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('active', sa.Boolean(), nullable=False, server_default='true'))


def downgrade():
    op.drop_column('users', 'active')
