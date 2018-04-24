# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add inbound_trip_id column to employee_travel_history

Revision ID: cef5b5166910
Revises: 41dce70220d3
Create Date: 2017-11-24 11:26:05.259529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cef5b5166910'
down_revision = '41dce70220d3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('employee_travel_history',
                  sa.Column('inbound_trip_id', sa.GUID(),
                            sa.ForeignKey('travels.id', ondelete='CASCADE'),
                            nullable=True))


def downgrade():
    op.drop_column('employee_travel_history', 'inbound_trip_id')
