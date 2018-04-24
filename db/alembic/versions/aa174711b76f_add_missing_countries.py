# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add missing countries

Revision ID: aa174711b76f
Revises: 636ba49911f3
Create Date: 2017-09-28 14:35:39.674836

"""
from uuid import uuid4
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa174711b76f'
down_revision = '636ba49911f3'
branch_labels = None
depends_on = None


def upgrade():
    countries = sa.table('countries',
                         sa.column('code', sa.String(3)),
                         sa.column('name', sa.String(100)))
    country_aliases = sa.table('country_aliases',
                               sa.column('id', sa.GUID),
                               sa.column('code', sa.String(3)),
                               sa.column('alias', sa.String(100)))
    op.bulk_insert(countries, [
        {'code': 'ANT', 'name': 'Netherlands Antilles'},
        {'code': 'SCG', 'name': 'Serbia and Montenegro'},
        {'code': 'XKX', 'name': 'Kosovo'},
    ])
    op.bulk_insert(country_aliases, [
        {'id': uuid4(), 'code': 'FJI', 'alias': 'FIJI'},
        {'id': uuid4(), 'code': 'LAO', 'alias': 'LAOS'},
        {'id': uuid4(), 'code': 'VGB', 'alias': 'British Virgin Islands'},
    ])


def downgrade():
    countries = sa.table('countries',
                         sa.column('code', sa.String(3)),
                         sa.column('name', sa.String(100)))
    country_aliases = sa.table('country_aliases',
                               sa.column('id', sa.GUID),
                               sa.column('code', sa.String(3)),
                               sa.column('alias', sa.String(100)))
    op.execute(countries.delete().where(countries.c.code.in_(['ANT', 'SCG', 'XKX'])))
    op.execute(country_aliases.delete() \
                              .where(country_aliases.c.alias.in_(['FIJI',
                                                                  'LAOS',
                                                                  'British Virgin Islands'])))
