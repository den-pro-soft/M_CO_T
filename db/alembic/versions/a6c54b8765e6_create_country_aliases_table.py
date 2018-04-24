# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create country aliases table

Revision ID: a6c54b8765e6
Revises: 5179394e5457
Create Date: 2017-09-01 16:12:03.502614

"""
from uuid import uuid4
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6c54b8765e6'
down_revision = '5179394e5457'
branch_labels = None
depends_on = None


def upgrade():
    country_aliases = op.create_table(
        'country_aliases',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('code', sa.String(3)),
        sa.Column('alias', sa.String(100), nullable=False),
    )
    op.bulk_insert(country_aliases, [
        {"id": uuid4(), "code": "USA", "alias": "UNITED STATES"},
        {"id": uuid4(), "code": "MAC", "alias": "MACAU"},
        {"id": uuid4(), "code": "TWN", "alias": "TAIWAN"},
        {"id": uuid4(), "code": "VNM", "alias": "VIETNAM"},
        {"id": uuid4(), "code": "GBR", "alias": "UNITED KINGDOM"},
        {"id": uuid4(), "code": "VIR", "alias": "U.S.VIRGIN ISLANDS"},
        {"id": uuid4(), "code": "KOR", "alias": "KOREA - REP. OF"},
    ])


def downgrade():
    op.drop_table('country_aliases')
