"""Track the processing of traveller data uploads"""

from sqlalchemy import Column, String, DateTime, Boolean
from .storage import db
from .custom_types import GUID


class TravellerData(db.Model):
    """TravellerData model class"""
    __tablename__ = 'traveller_data'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, upload_date, upload_key, filename, valid):
        self.id = pk
        self.customer_id = customer_id
        self.upload_date = upload_date
        self.upload_key = upload_key
        self.filename = filename
        self.valid = valid

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    customer_id = Column(GUID)
    upload_date = Column(DateTime)
    upload_key = Column(String)
    filename = Column(String)
    valid = Column(Boolean)
