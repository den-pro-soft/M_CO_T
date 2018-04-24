# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create table unclear_border_cross_clarifications

Revision ID: eb90a4a2c04d
Revises: 34a8b1080db4
Create Date: 2017-09-29 18:38:28.699057

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb90a4a2c04d'
down_revision = '34a8b1080db4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'border_cross_time_clarifications',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('customer_id', sa.GUID,
                  sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_name', sa.String(500), nullable=True),
        sa.Column('employee_id', sa.String(500), nullable=True),
        sa.Column('border_cross', sa.DateTime(), nullable=False),
        sa.Column('origin_country', sa.String(3), nullable=False),
        sa.Column('destination_country', sa.String(3), nullable=False),
        sa.Column('correct_time', sa.Time(), nullable=False),
    )


def downgrade():
    op.drop_table('border_cross_time_clarifications')
