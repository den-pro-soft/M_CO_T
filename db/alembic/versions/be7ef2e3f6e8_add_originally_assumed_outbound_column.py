# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add originally assumed outbound column

Revision ID: be7ef2e3f6e8
Revises: cef5b5166910
Create Date: 2017-11-24 11:46:24.651269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be7ef2e3f6e8'
down_revision = 'cef5b5166910'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('employee_travel_history', sa.Column('originally_assumed_outbound', sa.Boolean(),
                                                       nullable=False, server_default='false'))


def downgrade():
    op.drop_column('employee_travel_history', 'originally_assumed_outbound')
