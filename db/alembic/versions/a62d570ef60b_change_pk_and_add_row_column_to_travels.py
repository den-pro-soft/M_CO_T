# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""change pk and add row column to travels

Revision ID: a62d570ef60b
Revises: 764e685ffaf9
Create Date: 2017-09-13 14:38:37.173686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a62d570ef60b'
down_revision = '764e685ffaf9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('travels') as bop:
        bop.add_column(sa.Column('row', sa.Integer(), nullable=True))
        bop.add_column(sa.Column('invalid', sa.Boolean(), nullable=False))
        bop.drop_column('id')
        bop.add_column(sa.Column('id', sa.GUID))
        bop.create_primary_key('travels_pkey', ['id'])


def downgrade():
    with op.batch_alter_table('travels') as bop:
        bop.drop_column('row')
        bop.drop_column('invalid')
        bop.drop_column('id')
        bop.add_column(sa.Column('id', sa.Integer,
                                 autoincrement=True,
                                 primary_key=True))
        bop.create_primary_key('travels_pkey', ['id'])
