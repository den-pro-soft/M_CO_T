# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create assumptions table

Revision ID: 598547b98830
Revises: 595f8f83132f
Create Date: 2017-08-18 15:07:41.212415

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '598547b98830'
down_revision = '595f8f83132f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'assumptions',
        sa.Column('user_id', sa.GUID, sa.ForeignKey('users.id'), primary_key=True, nullable=False),
        sa.Column('outbound_uk_without_inbound', sa.String(1), nullable=False),
        sa.Column('business_trav_treaty_3159', sa.String(1), nullable=False),
        sa.Column('business_trav_treaty_60183', sa.String(1), nullable=False),
        sa.Column('use_demin_incidental_workdays', sa.Boolean(), nullable=False),
        sa.Column('deminimus_incidental_workdays', sa.Integer(), nullable=True),
        sa.Column('use_demin_eeaa1_workdays', sa.Boolean(), nullable=False),
        sa.Column('deminimus_eeaa1_workdays', sa.Integer(), nullable=True),
    )


def downgrade():
    op.drop_table('assumptions')
