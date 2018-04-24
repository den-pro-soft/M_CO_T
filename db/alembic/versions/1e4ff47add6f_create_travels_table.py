# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create travels table

Revision ID: 1e4ff47add6f
Revises: 780e4a67bc57
Create Date: 2017-08-24 10:38:47.500317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e4ff47add6f'
down_revision = '780e4a67bc57'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'travels',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('traveller_name', sa.String(500), nullable=True),
        sa.Column('employee_id', sa.String(500), nullable=True),
        sa.Column('employing_entity', sa.String(500), nullable=True),
        sa.Column('employee_country', sa.String(3), nullable=True),
        sa.Column('au', sa.String(500), nullable=True),
        sa.Column('booking_date', sa.Date(), nullable=True),
        sa.Column('record_locator', sa.String(500), nullable=True),
        sa.Column('ticket_no', sa.String(500), nullable=True),
        sa.Column('ticket_type', sa.String(500), nullable=True),
        sa.Column('segment_no', sa.String(500), nullable=True),
        sa.Column('calculated_seg_no', sa.String(500), nullable=True),
        sa.Column('origin_country_name', sa.String(3), nullable=True),
        sa.Column('origin_airport_code', sa.String(500), nullable=True),
        sa.Column('destination_country_name', sa.String(3), nullable=True),
        sa.Column('destination_airport_code', sa.String(500), nullable=True),
        sa.Column('routing_airports', sa.String(1000), nullable=True),
        sa.Column('departure_date', sa.Date(), nullable=True),
        sa.Column('departure_time', sa.Time(), nullable=True),
        sa.Column('arrival_date', sa.Date(), nullable=True),
        sa.Column('arrival_time', sa.Time(), nullable=True),
    )


def downgrade():
    op.drop_table('travels')
