# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create eth version column in customers table

Revision ID: 764e685ffaf9
Revises: f0477c8101b2
Create Date: 2017-09-12 15:52:57.672255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '764e685ffaf9'
down_revision = 'f0477c8101b2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('customers', sa.Column('employee_travel_history_version',
                                         sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('customers', 'employee_travel_history_version')
