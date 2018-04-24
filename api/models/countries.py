"""Country domain"""

from sqlalchemy import Column, String
from .storage import db
from .custom_types import GUID


class Country(db.Model):
    """Country model class"""
    __tablename__ = 'countries'

    # pylint: disable=C0103
    code = Column(String, primary_key=True)
    name = Column(String)


class CountryAlias(db.Model):
    """CountryAlias model class"""
    __tablename__ = 'country_aliases'

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    code = Column(String)
    alias = Column(String)
