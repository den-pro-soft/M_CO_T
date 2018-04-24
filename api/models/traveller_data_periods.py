"""Represents periods of traveller data"""

from sqlalchemy import Column, Date, ForeignKey
from sqlalchemy.orm import relationship, backref
from .storage import db
from .custom_types import GUID
from .traveller_data import TravellerData


class TravellerDataPeriod(db.Model):
    """TravellerDataPeriod model class"""
    __tablename__ = 'traveller_data_periods'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, from_date, to_date, traveller_data_id):
        self.id = pk
        self.customer_id = customer_id
        self.from_date = from_date
        self.to_date = to_date
        self.traveller_data_id = traveller_data_id

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    customer_id = Column(GUID)
    from_date = Column(Date)
    to_date = Column(Date)
    traveller_data_id = Column(GUID, ForeignKey('traveller_data.id'))
    traveller_data = relationship(TravellerData,
                                  backref=backref('traveller_data_periods',
                                                  lazy='raise',
                                                  cascade='all, delete-orphan'))
