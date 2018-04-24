# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create arrangement category index

Revision ID: f0477c8101b2
Revises: ff2383293d21
Create Date: 2017-09-06 11:31:58.509342

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f0477c8101b2'
down_revision = 'ff2383293d21'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('employee_arrangements_category_idx', 'employee_arrangements', ['category'])


def downgrade():
    op.drop_index('employee_arrangements_category_idx')
