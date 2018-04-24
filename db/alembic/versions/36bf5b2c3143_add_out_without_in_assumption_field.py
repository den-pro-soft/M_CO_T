# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add out without in assumption field

Revision ID: 36bf5b2c3143
Revises: 7d4f61caaaa2
Create Date: 2017-11-24 10:34:53.136742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36bf5b2c3143'
down_revision = '7d4f61caaaa2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('assumptions', sa.Column('inbound_uk_without_outbound',
                                           sa.String(1), nullable=False, server_default='1'))


def downgrade():
    op.drop_column('assumptions', 'inbound_uk_without_outbound')
