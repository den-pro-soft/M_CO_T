"""Information about Company Branches"""

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from .storage import db
from .custom_types import GUID
from .companies import Company


class Branch(db.Model):
    """Company Branch model class"""
    __tablename__ = 'branches'

    # pylint: disable=C0103
    def __init__(self, pk, company_id, name, country):
        self.id = pk
        self.company_id = company_id
        self.name = name
        self.country = country

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    company_id = Column(GUID, ForeignKey('companies.id'))
    company = relationship(Company, backref=backref('branches', lazy='raise'))
    name = Column(String)
    country = Column(String)
