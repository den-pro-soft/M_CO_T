# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add outbound_trip_id column to employee_travel_history

Revision ID: 8bb12e643c85
Revises: f568e0700e09
Create Date: 2017-10-04 15:48:15.619204

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bb12e643c85'
down_revision = 'f568e0700e09'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('employee_travel_history',
                  sa.Column('outbound_trip_id', sa.GUID(),
                            sa.ForeignKey('travels.id', ondelete='CASCADE'),
                            nullable=True))


def downgrade():
    op.drop_column('employee_travel_history', 'outbound_trip_id')
