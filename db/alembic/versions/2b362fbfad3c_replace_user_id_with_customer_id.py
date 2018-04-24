# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""replace user_id with customer_id

Revision ID: 2b362fbfad3c
Revises: f525f826bf2d
Create Date: 2017-08-29 21:16:48.353440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b362fbfad3c'
down_revision = 'f525f826bf2d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('assumptions', 'user_id')
    op.add_column('assumptions', sa.Column('customer_id', sa.GUID(),
                                           sa.ForeignKey('customers.id', ondelete='CASCADE'),
                                           nullable=False))
    op.drop_column('branches', 'user_id')
    op.drop_column('companies', 'user_id')
    op.add_column('companies', sa.Column('customer_id', sa.GUID(),
                                         sa.ForeignKey('customers.id', ondelete='CASCADE'),
                                         nullable=False))
    op.drop_column('companies_infos', 'user_id')
    op.add_column('companies_infos', sa.Column('customer_id', sa.GUID(),
                                               sa.ForeignKey('customers.id', ondelete='CASCADE'),
                                               nullable=False))
    op.drop_column('employee_spreadsheets', 'user_id')
    op.add_column('employee_spreadsheets', sa.Column('customer_id', sa.GUID(),
                                                     sa.ForeignKey('customers.id',
                                                                   ondelete='CASCADE'),
                                                     nullable=False))
    op.drop_column('traveller_data', 'user_id')
    op.add_column('traveller_data', sa.Column('customer_id', sa.GUID(),
                                              sa.ForeignKey('customers.id', ondelete='CASCADE'),
                                              nullable=False))
    op.drop_column('traveller_data_periods', 'user_id')
    op.add_column('traveller_data_periods', sa.Column('customer_id', sa.GUID(),
                                                      sa.ForeignKey('customers.id',
                                                                    ondelete='CASCADE'),
                                                      nullable=False))


def downgrade():
    op.drop_column('traveller_data_periods', 'customer_id')
    op.add_column('traveller_data_periods', sa.Column('user_id', sa.GUID(),
                                                      sa.ForeignKey('users.id',
                                                                    ondelete='CASCADE'),
                                                      nullable=False))
    op.drop_column('traveller_data', 'customer_id')
    op.add_column('traveller_data', sa.Column('user_id', sa.GUID(),
                                              sa.ForeignKey('users.id', ondelete='CASCADE'),
                                              nullable=False))
    op.drop_column('employee_spreadsheets', 'customer_id')
    op.add_column('employee_spreadsheets', sa.Column('user_id', sa.GUID(),
                                                     sa.ForeignKey('users.id', ondelete='CASCADE'),
                                                     nullable=False))
    op.drop_column('companies_infos', 'customer_id')
    op.add_column('companies_infos', sa.Column('user_id', sa.GUID(),
                                               sa.ForeignKey('users.id', ondelete='CASCADE'),
                                               nullable=False))
    op.drop_column('companies', 'customer_id')
    op.add_column('companies', sa.Column('user_id', sa.GUID(),
                                         sa.ForeignKey('users.id', ondelete='CASCADE'),
                                         nullable=False))
    op.add_column('branches', sa.Column('user_id', sa.GUID(),
                                        sa.ForeignKey('users.id', ondelete='CASCADE'),
                                        nullable=False))
    op.drop_column('assumptions', 'customer_id')
    op.add_column('assumptions', sa.Column('user_id', sa.GUID(),
                                           sa.ForeignKey('users.id', ondelete='CASCADE'),
                                           nullable=False))
