# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add ignored trips/employees tables

Revision ID: 5574c0ba5fdc
Revises: be7ef2e3f6e8
Create Date: 2017-11-29 08:57:42.479869

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5574c0ba5fdc'
down_revision = 'be7ef2e3f6e8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ignored_employees',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('customer_id', sa.GUID, sa.ForeignKey('customers.id')),
        sa.Column('traveller_name', sa.String(500), nullable=True),
        sa.Column('employee_id', sa.String(500), nullable=True),
    )
    op.create_table(
        'ignored_trips',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('customer_id', sa.GUID, sa.ForeignKey('customers.id')),
        sa.Column('traveller_name', sa.String(500), nullable=True),
        sa.Column('employee_id', sa.String(500), nullable=True),
        sa.Column('origin_country_name', sa.String(3), nullable=False),
        sa.Column('destination_country_name', sa.String(3), nullable=False),
        sa.Column('departure_date', sa.Date(), nullable=True),
        sa.Column('departure_time', sa.Time(), nullable=True),
        sa.Column('arrival_date', sa.Date(), nullable=True),
        sa.Column('arrival_time', sa.Time(), nullable=True),
    )


def downgrade():
    op.drop_table('ignored_trips')
    op.drop_table('ignored_employees')
