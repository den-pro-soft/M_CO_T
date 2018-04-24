# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create treaties table

Revision ID: b06847b06c4c
Revises: c08e5e5c0578
Create Date: 2017-09-15 09:27:47.187235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b06847b06c4c'
down_revision = 'c08e5e5c0578'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'treaties',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('country_code', sa.String(3), nullable=False),
        sa.Column('from_date', sa.Date(), nullable=False),
        sa.Column('to_date', sa.Date(), nullable=True),
    )


def downgrade():
    op.drop_table('treaties')
