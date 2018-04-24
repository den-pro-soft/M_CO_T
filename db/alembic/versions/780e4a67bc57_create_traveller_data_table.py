# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create traveller data table

Revision ID: 780e4a67bc57
Revises: 1cfbd0896037
Create Date: 2017-08-24 10:34:59.901393

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '780e4a67bc57'
down_revision = '1cfbd0896037'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'traveller_data',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('user_id', sa.GUID,
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('upload_date', sa.DateTime(), nullable=False),
        sa.Column('upload_key', sa.GUID, nullable=False),
        sa.Column('filename', sa.String(500), nullable=False),
    )


def downgrade():
    op.drop_table('traveller_data')
