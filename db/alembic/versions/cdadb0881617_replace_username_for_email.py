# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""replace username for email

Revision ID: cdadb0881617
Revises: 0ca0d6d314b5
Create Date: 2017-08-16 10:29:26.949829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdadb0881617'
down_revision = '0ca0d6d314b5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users') as bop:
        bop.drop_column('username')
        bop.add_column(sa.Column('email', sa.String(500), nullable=False, unique=True))


def downgrade():
    with op.batch_alter_table('users') as bop:
        bop.drop_column('email')
        bop.add_column(sa.Column('username', sa.String(50), nullable=False, unique=True))
