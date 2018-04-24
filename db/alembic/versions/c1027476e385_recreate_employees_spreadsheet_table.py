# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""recreate employees spreadsheet table

Revision ID: c1027476e385
Revises: 598547b98830
Create Date: 2017-08-21 11:04:44.375980

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1027476e385'
down_revision = '598547b98830'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('employee_spreadsheets')
    op.create_table(
        'employee_spreadsheets',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('user_id', sa.GUID,
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('upload_date', sa.DateTime(), nullable=False),
        sa.Column('uk_employees', sa.Integer, nullable=False),
        sa.Column('overseas_branch_employees', sa.Integer, nullable=False),
        sa.Column('uk_expatriates', sa.Integer, nullable=False),
        sa.Column('nt_sta_employees', sa.Integer, nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
    )


def downgrade():
    op.drop_table('employee_spreadsheets')
    op.create_table(
        'employee_spreadsheets',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('user_id', sa.GUID,
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('upload_key', sa.GUID, nullable=False),
        sa.Column('file_name', sa.String(500), nullable=False),
        sa.Column('upload_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(1), nullable=False),
    )
