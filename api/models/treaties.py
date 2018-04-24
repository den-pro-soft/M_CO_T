"""Treaty domain"""

from sqlalchemy import Column, String, Date
from .storage import db
from .custom_types import GUID


class Treaty(db.Model):
    """Treaty model class"""
    __tablename__ = 'treaties'

    # pylint: disable=C0103
    def __init__(self, pk, country_code, from_date, to_date):
        self.id = pk
        self.country_code = country_code
        self.from_date = from_date
        self.to_date = to_date

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    country_code = Column(String)
    from_date = Column(Date)
    to_date = Column(Date)
