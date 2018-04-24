# pylint: disable=C0103
# pylint: disable=C0111
# pylint: disable=E1101
"""remove employee_name from home and inbound clarifications

Revision ID: a12c059e23e3
Revises: 6f5bcf5e196e
Create Date: 2017-10-25 15:32:04.084302

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a12c059e23e3'
down_revision = '6f5bcf5e196e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('update home_country_clarifications set employee_id = employee_name ' +
               'where employee_id is null or employee_id = \'\'')
    op.alter_column('home_country_clarifications', 'employee_id',
                    new_column_name='effective_employee_id')
    op.drop_column('home_country_clarifications', 'employee_name')
    op.execute('update inbound_assumption_confirmations set employee_id = employee_name ' +
               'where employee_id is null or employee_id = \'\'')
    op.alter_column('inbound_assumption_confirmations', 'employee_id',
                    new_column_name='effective_employee_id')
    op.drop_column('inbound_assumption_confirmations', 'employee_name')


def downgrade():
    raise Exception('NOT SUPPORTED. This migration causes irreversible loss of data. ' +
                    'If you really need to rollback this, manually undo the operations ' +
                    'faking data where appropriate and comment this exception.')
