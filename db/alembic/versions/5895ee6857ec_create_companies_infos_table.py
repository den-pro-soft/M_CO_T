# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create companies_infos table

Revision ID: 5895ee6857ec
Revises: cdadb0881617
Create Date: 2017-08-16 13:08:59.850503

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5895ee6857ec'
down_revision = 'cdadb0881617'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'companies_infos',
        sa.Column('user_id', sa.GUID, sa.ForeignKey('users.id'), primary_key=True, nullable=False),
        sa.Column('branches_overseas', sa.Boolean(), nullable=False),
        sa.Column('simplified_annual_payroll', sa.Boolean(), nullable=False),
        sa.Column('employees_on_assignment_uk', sa.Boolean(), nullable=False),
        sa.Column('any_non_taxable_employees', sa.Boolean(), nullable=False),
    )


def downgrade():
    op.drop_table('companies_infos')
