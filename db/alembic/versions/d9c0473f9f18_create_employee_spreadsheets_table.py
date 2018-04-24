# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create employee spreadsheets table

Revision ID: d9c0473f9f18
Revises: 692680ef176c
Create Date: 2017-08-17 11:13:29.685335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9c0473f9f18'
down_revision = '692680ef176c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'employee_spreadsheets',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('user_id', sa.GUID,
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('upload_key', sa.GUID, nullable=False),
        sa.Column('status', sa.String(1), nullable=False),
    )


def downgrade():
    op.drop_table('employee_spreadsheets')
