"""Customer model related functions"""

from sqlalchemy import Column, String, DateTime, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from .storage import db
from .custom_types import GUID
from .applications import Application


CUSTOMER_APPLICATION_TABLE = Table('customer_application', db.Model.metadata,
                                   Column('customer_id', GUID, ForeignKey('customers.id')),
                                   Column('application_id', GUID, ForeignKey('applications.id')))


class Customer(db.Model):
    """Customer model class"""
    __tablename__ = 'customers'

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    name = Column(String)
    address = Column(String)
    contract_end_date = Column(DateTime)
    applications = relationship(Application,
                                secondary=CUSTOMER_APPLICATION_TABLE,
                                lazy='raise')
    active = Column(Boolean)
    last_travel_history_request = Column(DateTime)
    last_available_travel_history = Column(DateTime)
    last_travel_history_error = Column(DateTime)
