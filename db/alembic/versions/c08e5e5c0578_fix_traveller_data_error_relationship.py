# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""fix traveller data error relationship

Revision ID: c08e5e5c0578
Revises: a62d570ef60b
Create Date: 2017-09-13 14:43:10.798465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c08e5e5c0578'
down_revision = 'a62d570ef60b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('traveller_data_errors') as bop:
        bop.drop_column('row')
        bop.drop_column('traveller_data_id')
        bop.add_column(sa.Column('travel_id', sa.GUID(),
                                 sa.ForeignKey('travels.id', ondelete='CASCADE'),
                                 nullable=False))


def downgrade():
    with op.batch_alter_table('traveller_data_errors') as bop:
        bop.add_column(sa.Column('row', sa.Integer(), nullable=False))
        bop.drop_column('travel_id')
        bop.add_column(sa.Column('traveller_data_id', sa.GUID(),
                                 sa.ForeignKey('traveller_data.id',
                                               ondelete='CASCADE'),
                                 nullable=False))
