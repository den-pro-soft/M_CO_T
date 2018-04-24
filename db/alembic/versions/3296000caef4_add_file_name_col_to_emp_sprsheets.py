# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add file name col to emp sprsheets

Revision ID: 3296000caef4
Revises: d9c0473f9f18
Create Date: 2017-08-17 11:26:44.059946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3296000caef4'
down_revision = 'd9c0473f9f18'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('employee_spreadsheets', sa.Column('file_name', sa.String(500), nullable=False))


def downgrade():
    op.drop_column('employee_spreadsheets', 'file_name')
