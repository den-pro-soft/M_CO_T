# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create inbound assumptions table

Revision ID: 3c4ab8d99f22
Revises: 0965af191c33
Create Date: 2017-09-28 17:12:30.273492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c4ab8d99f22'
down_revision = '0965af191c33'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'inbound_assumption_confirmations',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('customer_id', sa.GUID,
                  sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_name', sa.String(500), nullable=True),
        sa.Column('employee_id', sa.String(500), nullable=True),
        sa.Column('to_date', sa.DateTime(), nullable=False),
        sa.Column('confirmed', sa.Boolean(), nullable=False),
        sa.Column('correct_date', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('inbound_assumption_confirmations')
