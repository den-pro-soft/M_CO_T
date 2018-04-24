# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create auth tokens table

Revision ID: 0ca0d6d314b5
Revises: bf0cc8187b7e
Create Date: 2017-08-15 10:34:14.215607

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ca0d6d314b5'
down_revision = 'bf0cc8187b7e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'auth_tokens',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('user_id', sa.GUID, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('issued_at', sa.DateTime(), nullable=False),
        sa.Column('last_heartbeat', sa.DateTime(), nullable=False)
    )


def downgrade():
    op.drop_table('auth_tokens')
