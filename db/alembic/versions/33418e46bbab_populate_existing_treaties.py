# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""populate existing treaties

Revision ID: 33418e46bbab
Revises: 288be55a070d
Create Date: 2017-09-15 12:15:07.026025

"""
from uuid import uuid4
from datetime import date
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33418e46bbab'
down_revision = '288be55a070d'
branch_labels = None
depends_on = None


def upgrade():
    treaties = sa.table('treaties',
                        sa.column('id', sa.GUID),
                        sa.column('country_code', sa.String(3)),
                        sa.column('from_date', sa.Date()),
                        sa.column('to_date', sa.Date()))
    countries = [
        'ALB',
        'DZA',
        'ATG',
        'ARG',
        'ARM',
        'AUS',
        'AUT',
        'AZE',
        'BHR',
        'BGD',
        'BRB',
        'BLR',
        'BEL',
        'BLZ',
        'BOL',
        'BIH',
        'BWA',
        'VGB',
        'BRN',
        'BGR',
        'CAN',
        'CYM',
        'CHL',
        'CHN',
        'CIV',
        'HRV',
        'CYP',
        'CZE',
        'DNK',
        'EGY',
        'EST',
        'ETH',
        'FLK',
        'FRO',
        'FJI',
        'FIN',
        'FRA',
        'GMB',
        'GEO',
        'DEU',
        'GHA',
        'GRC',
        'GRD',
        'GGY',
        'GUY',
        'HKG',
        'HUN',
        'ISL',
        'IND',
        'IDN',
        'IRL',
        'IMN',
        'ISR',
        'ITA',
        'JAM',
        'JPN',
        'JEY',
        'JOR',
        'KAZ',
        'KEN',
        'KIR',
        'UKN',
        'KWT',
        'LVA',
        'LSO',
        'LBY',
        'LIE',
        'LTU',
        'LUX',
        'MKD',
        'MWI',
        'MYS',
        'MLT',
        'MUS',
        'MEX',
        'MDA',
        'MNE',
        'MSR',
        'MAR',
        'MMR',
        'NAM',
        'NLD',
        'NZL',
        'NGA',
        'NOR',
        'OMN',
        'PAK',
        'PAN',
        'PNG',
        'PHL',
        'POL',
        'PRT',
        'QAT',
        'ROU',
        'RUS',
        'SAU',
        'SEN',
        'SRB',
        'SLE',
        'SGP',
        'SVK',
        'SVN',
        'SLB',
        'ZAF',
        'KOR',
        'ESP',
        'LKA',
        'KNA',
        'SDN',
        'SWZ',
        'SWE',
        'CHE',
        'TWN',
        'TJK',
        'THA',
        'TTO',
        'TUN',
        'TUR',
        'TKM',
        'TUV',
        'UGA',
        'UKR',
        'ARE',
        'GBR',
        'USA',
        'UZB',
        'VEN',
        'VNM',
        'ZMB',
        'ZWE',
        'URU',
    ]
    op.bulk_insert(treaties, [
        {'id': uuid4(), 'country_code': country, 'from_date': date(1, 1, 1), 'to_date': None}
        for country in countries
    ])


def downgrade():
    treaties = sa.table('treaties')
    op.execute(treaties.delete())
