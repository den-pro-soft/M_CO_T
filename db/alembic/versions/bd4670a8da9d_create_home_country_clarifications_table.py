# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create home country clarifications table

Revision ID: bd4670a8da9d
Revises: b06847b06c4c
Create Date: 2017-09-15 09:35:56.343830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd4670a8da9d'
down_revision = 'b06847b06c4c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'home_country_clarifications',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('customer_id', sa.GUID,
                  sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_name', sa.String(500), nullable=True),
        sa.Column('employee_id', sa.String(500), nullable=True),
        sa.Column('home_country', sa.String(3), nullable=False),
        sa.Column('from_date', sa.DateTime(), nullable=True),
        sa.Column('to_date', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('home_country_clarifications')
