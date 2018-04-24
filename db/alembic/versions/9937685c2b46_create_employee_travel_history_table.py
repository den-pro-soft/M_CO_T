# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create employee travel history table

Revision ID: 9937685c2b46
Revises: bd4670a8da9d
Create Date: 2017-09-15 09:50:11.426552

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9937685c2b46'
down_revision = 'bd4670a8da9d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'employee_travel_history',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('customer_id', sa.GUID,
                  sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_ts', sa.DateTime(), nullable=False),
        sa.Column('traveller_name', sa.String(500), nullable=True),
        sa.Column('employee_id', sa.String(500), nullable=True),
        sa.Column('category', sa.Integer(), nullable=False),
        sa.Column('from_date', sa.DateTime(), nullable=True),
        sa.Column('to_date', sa.DateTime(), nullable=True),
        sa.Column('originally_unclear', sa.Boolean(), nullable=False),
    )


def downgrade():
    op.drop_table('employee_travel_history')
