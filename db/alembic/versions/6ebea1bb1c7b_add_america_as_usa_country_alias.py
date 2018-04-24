# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add america as usa country alias

Revision ID: 6ebea1bb1c7b
Revises: eb90a4a2c04d
Create Date: 2017-10-03 11:17:41.049990

"""
from uuid import uuid4
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ebea1bb1c7b'
down_revision = 'eb90a4a2c04d'
branch_labels = None
depends_on = None


def upgrade():
    country_aliases = sa.table('country_aliases',
                               sa.column('id', sa.GUID),
                               sa.column('code', sa.String(3)),
                               sa.column('alias', sa.String(100)))
    op.bulk_insert(country_aliases, [
        {'id': uuid4(), 'code': 'USA', 'alias': 'AMERICA'},
    ])


def downgrade():
    country_aliases = sa.table('country_aliases',
                               sa.column('id', sa.GUID),
                               sa.column('code', sa.String(3)),
                               sa.column('alias', sa.String(100)))
    op.execute(country_aliases.delete() \
                              .where(country_aliases.c.alias.in_(['AMERICA'])))
