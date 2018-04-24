# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""drop report_results table

Revision ID: 12657ad7a58b
Revises: 704e90e214d1
Create Date: 2017-10-05 19:39:51.956158

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12657ad7a58b'
down_revision = '704e90e214d1'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('report_results')


def downgrade():
    op.create_table(
        'report_results',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('customer_id', sa.GUID,
                  sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_ts', sa.DateTime(), nullable=False),
        sa.Column('from_date', sa.DateTime(), nullable=True),
        sa.Column('to_date', sa.DateTime(), nullable=True),
        sa.Column('traveller_name', sa.String(500), nullable=True),
        sa.Column('employee_id', sa.String(500), nullable=True),
        sa.Column('category', sa.Integer(), nullable=False),
        sa.Column('days', sa.Integer(), nullable=False),
        sa.Column('monthly', sa.Boolean(), nullable=False, server_default='false'),
    )
