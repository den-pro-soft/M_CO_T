# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""replace user_id for sprdsheet_id on employees

Revision ID: c9430d4fb2ed
Revises: c1027476e385
Create Date: 2017-08-21 12:06:22.742668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9430d4fb2ed'
down_revision = '418bbe2cd3b2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('employees') as bop:
        bop.drop_column('user_id')
        bop.add_column(sa.Column('employee_spreadsheet_id', sa.GUID(),
                                 sa.ForeignKey('employee_spreadsheets.id', ondelete='CASCADE'),
                                 nullable=False))


def downgrade():
    with op.batch_alter_table('employees') as bop:
        bop.drop_column('employee_spreadsheet_id')
        bop.add_column(sa.Column('user_id', sa.GUID(),
                                 sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False))
