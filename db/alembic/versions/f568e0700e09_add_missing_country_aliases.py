# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""add missing country aliases

Revision ID: f568e0700e09
Revises: 6ebea1bb1c7b
Create Date: 2017-10-04 14:58:28.215857

"""
from uuid import uuid4
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f568e0700e09'
down_revision = '6ebea1bb1c7b'
branch_labels = None
depends_on = None


def upgrade():
    country_aliases = sa.table('country_aliases',
                               sa.column('id', sa.GUID),
                               sa.column('code', sa.String(3)),
                               sa.column('alias', sa.String(100)))
    # pylint: disable=C0301
    op.bulk_insert(country_aliases, [
        {'id': uuid4(), 'code': 'BOL', 'alias': 'Bolivia'}, # Bolivia (Plurinational State of)
        {'id': uuid4(), 'code': 'CCK', 'alias': 'Cocos Islands'}, # Cocos Islands
        {'id': uuid4(), 'code': 'CIV', 'alias': 'Ivory Coast'}, # Côte d'Ivoire
        {'id': uuid4(), 'code': 'CIV', 'alias': 'Cote d’Ivoire'}, # Côte d'Ivoire
        {'id': uuid4(), 'code': 'CIV', 'alias': 'Cote d\'Ivoire'}, # Côte d'Ivoire
        {'id': uuid4(), 'code': 'FLK', 'alias': 'Falkland Islands'}, # Falkland Islands (Malvinas)
        {'id': uuid4(), 'code': 'FLK', 'alias': 'Malvinas'}, # Falkland Islands (Malvinas)
        {'id': uuid4(), 'code': 'FJI', 'alias': 'Fiji Islands'}, # Fiji
        {'id': uuid4(), 'code': 'IRN', 'alias': 'Iran'}, # Iran (Islamic Republic of)
        {'id': uuid4(), 'code': 'IRN', 'alias': 'Iran'}, # Iran (Islamic Republic of)
        {'id': uuid4(), 'code': 'PKR', 'alias': 'North Korea'}, # Korea (Democratic People's Republic of)
        {'id': uuid4(), 'code': 'KOR', 'alias': 'South Korea'}, # Korea (Republic of)
        {'id': uuid4(), 'code': 'MKD', 'alias': 'Macedonia'}, # Macedonia (the former Yugoslav Republic of)
        {'id': uuid4(), 'code': 'FSM', 'alias': 'Micronesia'}, # Micronesia (Federated States of)
        {'id': uuid4(), 'code': 'MDA', 'alias': 'Moldova'}, # Moldova (Republic of)
        {'id': uuid4(), 'code': 'PSE', 'alias': 'Palestine'}, # Palestine, State of
        {'id': uuid4(), 'code': 'RUS', 'alias': 'Russia'}, # Russian Federation
        {'id': uuid4(), 'code': 'BLM', 'alias': 'St Barthélemy'}, # Saint Barthélemy
        {'id': uuid4(), 'code': 'BLM', 'alias': 'St. Barthélemy'}, # Saint Barthélemy
        {'id': uuid4(), 'code': 'SHN', 'alias': 'St Helena, Ascension and Tristan da Cunha'}, # Saint Helena, Ascension and Tristan da Cunha
        {'id': uuid4(), 'code': 'SHN', 'alias': 'St. Helena, Ascension and Tristan da Cunha'}, # Saint Helena, Ascension and Tristan da Cunha
        {'id': uuid4(), 'code': 'KNA', 'alias': 'St Kitts and Nevis'}, # Saint Kitts and Nevis
        {'id': uuid4(), 'code': 'KNA', 'alias': 'St. Kitts and Nevis'}, # Saint Kitts and Nevis
        {'id': uuid4(), 'code': 'LCA', 'alias': 'St Lucia'}, # Saint Lucia
        {'id': uuid4(), 'code': 'LCA', 'alias': 'St. Lucia'}, # Saint Lucia
        {'id': uuid4(), 'code': 'MAF', 'alias': 'Saint Martin'}, # Saint Martin (French part)
        {'id': uuid4(), 'code': 'MAF', 'alias': 'St Martin'}, # Saint Martin (French part)
        {'id': uuid4(), 'code': 'MAF', 'alias': 'St. Martin'}, # Saint Martin (French part)
        {'id': uuid4(), 'code': 'SPM', 'alias': 'St Pierre and Miquelon'}, # Saint Pierre and Miquelon
        {'id': uuid4(), 'code': 'SPM', 'alias': 'St. Pierre and Miquelon'}, # Saint Pierre and Miquelon
        {'id': uuid4(), 'code': 'VCT', 'alias': 'St Vincent and the Grenadines'}, # Saint Vincent and the Grenadines
        {'id': uuid4(), 'code': 'VCT', 'alias': 'St. Vincent and the Grenadines'}, # Saint Vincent and the Grenadines
        {'id': uuid4(), 'code': 'SXM', 'alias': 'Sint Maarten'}, # Sint Maarten (Dutch part)
        {'id': uuid4(), 'code': 'SYR', 'alias': 'Syria'}, # Syrian Arab Republic
        {'id': uuid4(), 'code': 'TZA', 'alias': 'Tanzania'}, # Tanzania, United Republic of
        {'id': uuid4(), 'code': 'VEN', 'alias': 'Venezuela'}, # Venezuela (Bolivarian Republic of)
        {'id': uuid4(), 'code': 'PRK', 'alias': 'N. Korea'}, # Korea (Democratic People's Republic of)
        {'id': uuid4(), 'code': 'KOR', 'alias': 'S. Korea'}, # Korea (Republic of)
        {'id': uuid4(), 'code': 'ZAF', 'alias': 'S. Africa'}, # South Africa
        {'id': uuid4(), 'code': 'SGS', 'alias': 'S. Georgia and the S. Sandwich Islands'}, # South Georgia and the South Sandwich Islands
        {'id': uuid4(), 'code': 'SSD', 'alias': 'S. Sudan'}, # South Sudan
    ])


def downgrade():
    country_aliases = sa.table('country_aliases',
                               sa.column('id', sa.GUID),
                               sa.column('code', sa.String(3)),
                               sa.column('alias', sa.String(100)))
    op.execute(country_aliases.delete() \
                              .where(country_aliases.c.alias.in_([
                                  'Bolivia',
                                  'Cocos Islands',
                                  'Ivory Coast',
                                  'Cote d’Ivoire',
                                  'Cote d\'Ivoire',
                                  'Falkland Islands',
                                  'Malvinas',
                                  'Fiji Islands',
                                  'Iran',
                                  'Iran',
                                  'North Korea',
                                  'South Korea',
                                  'Macedonia',
                                  'Micronesia',
                                  'Moldova',
                                  'Palestine',
                                  'Russia',
                                  'St Barthélemy',
                                  'St. Barthélemy',
                                  'St Helena, Ascension and Tristan da Cunha',
                                  'St. Helena, Ascension and Tristan da Cunha',
                                  'St Kitts and Nevis',
                                  'St. Kitts and Nevis',
                                  'St Lucia',
                                  'St. Lucia',
                                  'Saint Martin',
                                  'St Martin',
                                  'St. Martin',
                                  'St Pierre and Miquelon',
                                  'St. Pierre and Miquelon',
                                  'St Vincent and the Grenadines',
                                  'St. Vincent and the Grenadines',
                                  'Sint Maarten',
                                  'Syria',
                                  'Tanzania',
                                  'Venezuela',
                                  'N. Korea',
                                  'S. Korea',
                                  'S. Africa',
                                  'S. Georgia and the S. Sandwich Islands',
                                  'S. Sudan',
                              ])))
