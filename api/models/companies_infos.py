"""Single per-user record table containing general
information regarding companies"""

from sqlalchemy import Column, Boolean
from .storage import db
from .custom_types import GUID


class CompaniesInfo(db.Model):
    """CompaniesInfo model class"""
    __tablename__ = 'companies_infos'

    def __init__(self, customer_id, branches_overseas, simplified_annual_payroll,
                 employees_on_assignment_uk, any_non_taxable_employees):
        self.customer_id = customer_id
        self.branches_overseas = branches_overseas
        self.simplified_annual_payroll = simplified_annual_payroll
        self.employees_on_assignment_uk = employees_on_assignment_uk
        self.any_non_taxable_employees = any_non_taxable_employees

    customer_id = Column(GUID, primary_key=True)
    branches_overseas = Column(Boolean, nullable=False)
    simplified_annual_payroll = Column(Boolean, nullable=False)
    employees_on_assignment_uk = Column(Boolean, nullable=False)
    any_non_taxable_employees = Column(Boolean, nullable=False)
