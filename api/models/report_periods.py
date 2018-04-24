"""ReportPeriod model related functions"""

from sqlalchemy import Column, ForeignKey, Date, Integer
from sqlalchemy.orm import relationship
from .storage import db
from .custom_types import GUID
from .users import User


class ReportPeriod(db.Model):
    """ReportPeriod model class"""
    __tablename__ = 'report_periods'

    # pylint: disable=C0103
    def __init__(self, pk, user_id, treaty_position, from_date, to_date):
        self.id = pk
        self.user_id = user_id
        self.treaty_position = treaty_position
        self.from_date = from_date
        self.to_date = to_date

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)

    user_id = Column(GUID, ForeignKey('users.id'), nullable=False)
    user = relationship(User)

    treaty_position = Column(Integer, nullable=False)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)
