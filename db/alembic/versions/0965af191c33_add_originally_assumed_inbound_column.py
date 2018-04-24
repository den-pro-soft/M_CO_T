# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add originally assumed inbound column

Revision ID: 0965af191c33
Revises: aa174711b76f
Create Date: 2017-09-28 15:37:15.883800

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0965af191c33'
down_revision = 'aa174711b76f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('employee_travel_history', sa.Column('originally_assumed_inbound', sa.Boolean(),
                                                       nullable=False, server_default='false'))


def downgrade():
    op.drop_column('employee_travel_history', 'originally_assumed_inbound')
