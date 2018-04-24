"""Information about Companies"""

from sqlalchemy import Column, Boolean, String
from .storage import db
from .custom_types import GUID


class Company(db.Model):
    """Company model class"""
    __tablename__ = 'companies'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, name, paye, tracking_method,
                 other_tracking_method, simplified_payroll,
                 simplified_payroll_paye):
        self.id = pk
        self.customer_id = customer_id
        self.name = name
        self.paye = paye
        self.tracking_method = tracking_method
        self.other_tracking_method = other_tracking_method
        self.simplified_payroll = simplified_payroll
        self.simplified_payroll_paye = simplified_payroll_paye

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    customer_id = Column(GUID)
    name = Column(String)
    paye = Column(String)
    tracking_method = Column(String)
    other_tracking_method = Column(String)
    simplified_payroll = Column(Boolean)
    simplified_payroll_paye = Column(String)
