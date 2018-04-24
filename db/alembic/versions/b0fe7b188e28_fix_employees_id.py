# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""fix employees id

Revision ID: b0fe7b188e28
Revises: e05226a23214
Create Date: 2017-08-31 13:21:04.866178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0fe7b188e28'
down_revision = '0acf188823eb'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('employees', 'id')
    op.add_column('employees', sa.Column('id', sa.GUID))
    op.create_primary_key('employees_pkey', 'employees', ['id'])


def downgrade():
    op.drop_column('employees', 'id')
    op.add_column('employees', sa.Column('id', sa.Integer,
                                         autoincrement=True,
                                         primary_key=True))
    op.create_primary_key('employees_pkey', 'employees', ['id'])
