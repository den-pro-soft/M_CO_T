# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create report_periods table

Revision ID: 6f5bcf5e196e
Revises: 12657ad7a58b
Create Date: 2017-10-23 22:47:48.351634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6f5bcf5e196e'
down_revision = '12657ad7a58b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'report_periods',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('user_id', sa.GUID, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('treaty_position', sa.Integer(), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=False)
    )


def downgrade():
    op.drop_table('report_periods')
