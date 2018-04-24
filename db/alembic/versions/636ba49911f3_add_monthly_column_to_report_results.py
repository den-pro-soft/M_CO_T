# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add monthly column to report results

Revision ID: 636ba49911f3
Revises: 66491409f517
Create Date: 2017-09-15 16:07:46.967325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '636ba49911f3'
down_revision = '66491409f517'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('report_results', sa.Column('monthly', sa.Boolean(),
                                              nullable=False, server_default='false'))


def downgrade():
    op.drop_column('report_results', 'monthly')
