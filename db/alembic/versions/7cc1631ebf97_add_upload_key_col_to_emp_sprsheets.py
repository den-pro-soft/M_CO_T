# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add upload key col to emp sprsheets

Revision ID: 7cc1631ebf97
Revises: 594988708d8e
Create Date: 2017-08-28 19:26:19.241316

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cc1631ebf97'
down_revision = '594988708d8e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('employee_spreadsheets', sa.Column('upload_key', sa.GUID(), nullable=False))


def downgrade():
    op.drop_column('employee_spreadsheets', 'upload_key')
