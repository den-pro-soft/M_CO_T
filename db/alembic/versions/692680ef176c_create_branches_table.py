# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create branches table

Revision ID: 692680ef176c
Revises: 75f775498a51
Create Date: 2017-08-16 13:30:21.368735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '692680ef176c'
down_revision = '75f775498a51'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'branches',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('user_id', sa.GUID,
                  sa.ForeignKey('users.id', ondelete="CASCADE"), nullable=False),
        sa.Column('company_id', sa.GUID,
                  sa.ForeignKey('companies.id', ondelete="CASCADE"), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('country', sa.String(3), nullable=False),
    )


def downgrade():
    op.drop_table('branches')
