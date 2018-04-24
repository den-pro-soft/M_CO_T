# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create border_cross column on travels table

Revision ID: 34a8b1080db4
Revises: 3c4ab8d99f22
Create Date: 2017-09-29 14:41:33.407426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34a8b1080db4'
down_revision = '3c4ab8d99f22'
branch_labels = None
depends_on = None


def upgrade():
    travels = sa.table('travels',
                       sa.column('origin_country_name', sa.String(3)),
                       sa.column('destination_country_name', sa.String(3)),
                       sa.column('departure_date', sa.Date()),
                       sa.column('departure_time', sa.Time()),
                       sa.column('arrival_date', sa.Date()),
                       sa.column('arrival_time', sa.Time()),
                       sa.column('border_cross', sa.DateTime()))
    op.add_column('travels', sa.Column('border_cross', sa.DateTime(), nullable=True))
    op.execute(travels.update() \
                      .values(border_cross=travels.c.departure_date + travels.c.departure_time) \
                      .where(travels.c.origin_country_name == 'GBR'))
    op.execute(travels.update() \
                      .values(border_cross=travels.c.arrival_date + travels.c.arrival_time) \
                      .where(travels.c.destination_country_name == 'GBR'))


def downgrade():
    op.drop_column('travels', 'border_cross')
