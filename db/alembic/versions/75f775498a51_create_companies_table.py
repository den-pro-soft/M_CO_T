# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create companies table

Revision ID: 75f775498a51
Revises: 5895ee6857ec
Create Date: 2017-08-16 13:20:57.085260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75f775498a51'
down_revision = '5895ee6857ec'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'companies',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('user_id', sa.GUID, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('paye', sa.String(50), nullable=False),
        sa.Column('tracking_method', sa.String(1), nullable=False),
        sa.Column('other_tracking_method', sa.String(50)),
        sa.Column('simplified_payroll', sa.Boolean(), nullable=False),
        sa.Column('simplified_payroll_paye', sa.String(50)),
    )


def downgrade():
    op.drop_table('companies')
