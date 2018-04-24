# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create report results table

Revision ID: 288be55a070d
Revises: 9937685c2b46
Create Date: 2017-09-15 10:06:34.328951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '288be55a070d'
down_revision = '9937685c2b46'
branch_labels = None
depends_on = None


def upgrade():
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
    )


def downgrade():
    op.drop_table('report_results')
