# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create employees table

Revision ID: 418bbe2cd3b2
Revises: c9430d4fb2ed
Create Date: 2017-08-22 00:42:57.650854

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '418bbe2cd3b2'
down_revision = 'c1027476e385'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('user_id', sa.GUID, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('name', sa.String(500), nullable=True),
        sa.Column('employee_id', sa.String(500), nullable=True),
    )


def downgrade():
    op.drop_table('employees')
