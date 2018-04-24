# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create effective period columns

Revision ID: 5179394e5457
Revises: e05226a23214
Create Date: 2017-08-31 14:13:06.758797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5179394e5457'
down_revision = 'e05226a23214'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('employee_arrangements') as bop:
        bop.add_column(sa.Column('effective_from', sa.Date))
        bop.add_column(sa.Column('effective_to', sa.Date))


def downgrade():
    with op.batch_alter_table('employee_arrangements') as bop:
        bop.drop_column('effective_from')
        bop.drop_column('effective_to')
