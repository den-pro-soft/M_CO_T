# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create same_person_confirmations table

Revision ID: 7d4f61caaaa2
Revises: a12c059e23e3
Create Date: 2017-10-25 18:36:59.933746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d4f61caaaa2'
down_revision = 'a12c059e23e3'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'same_person_confirmations',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('customer_id', sa.GUID,
                  sa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('effective_employee_id', sa.String(500), nullable=False),
    )


def downgrade():
    op.drop_table('same_person_confirmations')
