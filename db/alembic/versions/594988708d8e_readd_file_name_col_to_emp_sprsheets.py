# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""readd file name col to emp sprsheets

Revision ID: 594988708d8e
Revises: 64567087ebf0
Create Date: 2017-08-28 19:09:42.499849

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '594988708d8e'
down_revision = '64567087ebf0'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('employee_spreadsheets', sa.Column('file_name', sa.String(500), nullable=False))


def downgrade():
    op.drop_column('employee_spreadsheets', 'file_name')
