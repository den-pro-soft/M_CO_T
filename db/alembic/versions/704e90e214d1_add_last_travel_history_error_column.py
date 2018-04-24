# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add last_travel_history_error column

Revision ID: 704e90e214d1
Revises: 8bb12e643c85
Create Date: 2017-10-05 12:03:19.791388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '704e90e214d1'
down_revision = '8bb12e643c85'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('customers', sa.Column('last_travel_history_error',
                                         sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('customers', 'last_travel_history_error')
