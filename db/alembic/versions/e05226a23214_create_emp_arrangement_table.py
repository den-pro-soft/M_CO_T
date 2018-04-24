# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create emp arrangement table

Revision ID: e05226a23214
Revises: 0acf188823eb
Create Date: 2017-08-31 13:13:22.435177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e05226a23214'
down_revision = 'b0fe7b188e28'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'employee_arrangements',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('employee_id', sa.GUID,
                  sa.ForeignKey('employees.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('category', sa.Integer(), nullable=False),
    )


def downgrade():
    op.drop_table('employee_arrangements')
