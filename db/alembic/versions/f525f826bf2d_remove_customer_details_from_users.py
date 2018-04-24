# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""remove customer details from users

Revision ID: f525f826bf2d
Revises: 771d7d68d3bd
Create Date: 2017-08-29 15:51:50.958326

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f525f826bf2d'
down_revision = '771d7d68d3bd'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users') as bop:
        bop.drop_column('contract_end_date')
        bop.drop_column('company_address')
        bop.drop_column('company_name')
        bop.add_column(sa.Column('customer_id', sa.GUID,
                                 sa.ForeignKey('customers.id'), nullable=False))


def downgrade():
    with op.batch_alter_table('users') as bop:
        bop.drop_column('customer_id')
        bop.add_column(sa.Column('company_name', sa.String(50), nullable=True))
        bop.add_column(sa.Column('company_address', sa.String(4000), nullable=True))
        bop.add_column(sa.Column('contract_end_date', sa.DateTime(), nullable=True))
