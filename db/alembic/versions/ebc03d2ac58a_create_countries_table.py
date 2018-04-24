# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create countries table

Revision ID: ebc03d2ac58a
Revises: c65842358319
Create Date: 2017-08-17 15:27:30.488286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ebc03d2ac58a'
down_revision = 'c65842358319'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'countries',
        sa.Column('code', sa.String(3), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
    )


def downgrade():
    op.drop_table('countries')
