# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add admin column to users table

Revision ID: f779f40a2452
Revises: b04ec01e4793
Create Date: 2017-08-23 12:01:07.328141

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f779f40a2452'
down_revision = 'b04ec01e4793'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('admin', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('users', 'admin')
