# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add valid column to traveller_data table

Revision ID: 5cc843a72537
Revises: dbcda4a9c8e1
Create Date: 2017-08-24 13:55:12.997585

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5cc843a72537'
down_revision = 'dbcda4a9c8e1'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('traveller_data', sa.Column('valid', sa.Boolean(),
                                              nullable=False, server_default='false'))


def downgrade():
    op.drop_column('traveller_data', 'valid')
