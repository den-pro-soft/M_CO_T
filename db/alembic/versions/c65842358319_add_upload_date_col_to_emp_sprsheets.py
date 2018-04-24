# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add upload date col to emp sprsheets

Revision ID: c65842358319
Revises: 3296000caef4
Create Date: 2017-08-17 11:45:24.690029

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c65842358319'
down_revision = '3296000caef4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('employee_spreadsheets', sa.Column('upload_date', sa.DateTime(), nullable=False))


def downgrade():
    op.drop_column('employee_spreadsheets', 'upload_date')
