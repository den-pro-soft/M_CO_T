# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add unsucessful login attemps

Revision ID: ececfd045b02
Revises: 5cc843a72537
Create Date: 2017-08-28 11:52:54.926661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ececfd045b02'
down_revision = '5cc843a72537'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('unsucessful_login_attemps',
                                     sa.Integer(),
                                     nullable=False,
                                     server_default='0'))


def downgrade():
    op.drop_column('users', 'unsucessful_login_attemps')
