# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add detailed user fields

Revision ID: b04ec01e4793
Revises: c9430d4fb2ed
Create Date: 2017-08-22 16:00:49.941124

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b04ec01e4793'
down_revision = 'c9430d4fb2ed'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users') as bop:
        bop.add_column(sa.Column('secondname', sa.String(50), nullable=True))
        bop.add_column(sa.Column('company_name', sa.String(50), nullable=True))
        bop.add_column(sa.Column('company_address', sa.String(4000), nullable=True))
        bop.add_column(sa.Column('contract_end_date', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('users') as bop:
        bop.drop_column('contract_end_date')
        bop.drop_column('company_address')
        bop.drop_column('company_name')
        bop.drop_column('secondname')
