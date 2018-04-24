# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""remove number column from traveller data period

Revision ID: ff2383293d21
Revises: 2413ad61f0a0
Create Date: 2017-09-05 12:57:32.961799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff2383293d21'
down_revision = '2413ad61f0a0'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('traveller_data_periods', 'number')


def downgrade():
    op.add_column('traveller_data_periods', sa.Column('number', sa.Integer(), nullable=False))
