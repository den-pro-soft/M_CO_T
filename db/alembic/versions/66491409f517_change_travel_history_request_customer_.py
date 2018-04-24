# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""change travel history request customer columns

Revision ID: 66491409f517
Revises: 33418e46bbab
Create Date: 2017-09-15 12:50:58.461495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66491409f517'
down_revision = '33418e46bbab'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('customers', 'employee_travel_history_version',
                    new_column_name='last_travel_history_request')
    op.add_column('customers', sa.Column('last_available_travel_history',
                                         sa.DateTime(), nullable=True))


def downgrade():
    op.alter_column('customers', 'last_travel_history_request',
                    new_column_name='employee_travel_history_version')
    op.drop_column('customers', 'last_available_travel_history')
