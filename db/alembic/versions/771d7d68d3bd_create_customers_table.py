# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create customers table

Revision ID: 771d7d68d3bd
Revises: 7cc1631ebf97
Create Date: 2017-08-29 15:27:47.199099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '771d7d68d3bd'
down_revision = '7cc1631ebf97'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'customers',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('address', sa.String(4000), nullable=True),
        sa.Column('contract_end_date', sa.DateTime(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
    )


def downgrade():
    op.drop_table('customers')
