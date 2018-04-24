# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add outbound assumption confirmations table

Revision ID: 41dce70220d3
Revises: 36bf5b2c3143
Create Date: 2017-11-24 10:38:08.565107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41dce70220d3'
down_revision = '36bf5b2c3143'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'outbound_assumption_confirmations',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('customer_id', sa.GUID,
                  sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('effective_employee_id', sa.String(500), nullable=True),
        sa.Column('from_date', sa.DateTime(), nullable=False),
        sa.Column('confirmed', sa.Boolean(), nullable=False),
        sa.Column('correct_date', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('outbound_assumption_confirmations')
