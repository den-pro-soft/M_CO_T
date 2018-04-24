# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create traveller_data_errors table

Revision ID: dbcda4a9c8e1
Revises: 9a4285be2695
Create Date: 2017-08-24 13:49:39.648102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbcda4a9c8e1'
down_revision = '9a4285be2695'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'traveller_data_errors',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('traveller_data_id', sa.GUID,
                  sa.ForeignKey('traveller_data.id', ondelete='CASCADE'), nullable=True),
        sa.Column('row', sa.Integer(), nullable=False),
        sa.Column('error_code', sa.Integer(), nullable=False),
    )


def downgrade():
    op.drop_table('traveller_data_errors')
