# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create traveller_data_periods table

Revision ID: 9a4285be2695
Revises: 6c6ba510ee9f
Create Date: 2017-08-24 12:58:41.074047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a4285be2695'
down_revision = '6c6ba510ee9f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'traveller_data_periods',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('user_id', sa.GUID,
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('number', sa.Integer(), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=False),
        sa.Column('traveller_data_id', sa.GUID,
                  sa.ForeignKey('traveller_data.id', ondelete='CASCADE'), nullable=True),
    )


def downgrade():
    op.drop_table('traveller_data_periods')
