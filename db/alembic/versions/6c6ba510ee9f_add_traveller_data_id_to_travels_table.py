# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add traveller_data_id to travels table

Revision ID: 6c6ba510ee9f
Revises: 1e4ff47add6f
Create Date: 2017-08-24 10:57:24.462281

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6c6ba510ee9f'
down_revision = '1e4ff47add6f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('travels', sa.Column('traveller_data_id', sa.GUID(),
                                       sa.ForeignKey('traveller_data.id', ondelete='CASCADE'),
                                       nullable=False))


def downgrade():
    op.drop_column('travels', 'traveller_data_id')
