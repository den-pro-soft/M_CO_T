# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""create applications table

Revision ID: 2413ad61f0a0
Revises: a6c54b8765e6
Create Date: 2017-09-05 10:13:00.899310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2413ad61f0a0'
down_revision = 'a6c54b8765e6'
branch_labels = None
depends_on = None


def upgrade():
    apps = op.create_table(
        'applications',
        sa.Column('id', sa.GUID, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
    )
    op.bulk_insert(apps, [
        {"name": "MinTax for business travellers", "id": "39082041-08f3-44ec-a692-c637f55ecdbf"},
        {"name": "MinTax for expense analysis", "id": "fd17e30e-4954-4b60-8e8f-d7e1d3ea58b5"},
    ])
    op.create_table(
        'customer_application',
        sa.Column('customer_id', sa.GUID,
                  sa.ForeignKey('customers.id'),
                  primary_key=True),
        sa.Column('application_id', sa.GUID,
                  sa.ForeignKey('applications.id', ondelete='CASCADE'),
                  primary_key=True),
    )


def downgrade():
    op.drop_table('customer_application')
    op.drop_table('applications')
