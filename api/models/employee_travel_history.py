"""Represents the result of traveller data processing"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .storage import db
from .custom_types import GUID
from .travels import Travel


class EmployeeTravelHistory(db.Model):
    """EmployeeTravelHistory model class"""
    __tablename__ = 'employee_travel_history'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, version_ts, traveller_name, employee_id,
                 category, from_date, to_date, originally_unclear, originally_assumed_inbound):
        self.id = pk
        self.customer_id = customer_id
        self.version_ts = version_ts
        self.traveller_name = traveller_name
        self.employee_id = employee_id
        self.category = category
        self.from_date = from_date
        self.to_date = to_date
        self.originally_unclear = originally_unclear
        self.originally_assumed_inbound = originally_assumed_inbound

    # pylint: disable=C0103
    id = Column(Integer, primary_key=True)
    customer_id = Column(GUID)
    version_ts = Column(DateTime)
    traveller_name = Column(String)
    employee_id = Column(String)
    category = Column(Integer)
    from_date = Column(DateTime)
    to_date = Column(DateTime)
    originally_unclear = Column(Boolean)
    originally_assumed_inbound = Column(Boolean)
    originally_assumed_outbound = Column(Boolean)
    outbound_trip_id = Column(GUID, ForeignKey('travels.id'))
    outbound_trip = relationship(Travel, lazy='raise', foreign_keys=[outbound_trip_id])
    inbound_trip_id = Column(GUID, ForeignKey('travels.id'))
    inbound_trip = relationship(Travel, lazy='raise', foreign_keys=[inbound_trip_id])
