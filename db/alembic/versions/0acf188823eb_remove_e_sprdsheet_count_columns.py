# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""remove e sprdsheet count columns

Revision ID: 0acf188823eb
Revises: 2b362fbfad3c
Create Date: 2017-08-31 13:08:21.053910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0acf188823eb'
down_revision = '2b362fbfad3c'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('employee_spreadsheets') as bop:
        bop.drop_column('uk_employees')
        bop.drop_column('overseas_branch_employees')
        bop.drop_column('uk_expatriates')
        bop.drop_column('nt_sta_employees')


def downgrade():
    with op.batch_alter_table('employee_spreadsheets') as bop:
        bop.add_column(sa.Column('uk_employees', sa.Integer, nullable=False))
        bop.add_column(sa.Column('overseas_branch_employees', sa.Integer, nullable=False))
        bop.add_column(sa.Column('uk_expatriates', sa.Integer, nullable=False))
        bop.add_column(sa.Column('nt_sta_employees', sa.Integer, nullable=False))
