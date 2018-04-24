# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""increase traveller data country name size

Revision ID: 64567087ebf0
Revises: ececfd045b02
Create Date: 2017-08-28 15:30:21.420283

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64567087ebf0'
down_revision = 'ececfd045b02'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('travels') as bop:
        bop.alter_column('employee_country', type_=sa.String(100))
        bop.alter_column('origin_country_name', type_=sa.String(100))
        bop.alter_column('destination_country_name', type_=sa.String(100))


def downgrade():
    with op.batch_alter_table('travels') as bop:
        bop.alter_column('destination_country_name', type_=sa.String(3))
        bop.alter_column('origin_country_name', type_=sa.String(3))
        bop.alter_column('employee_country', type_=sa.String(3))
