"""Application domain"""

from uuid import UUID
from sqlalchemy import Column, String
from .storage import db
from .custom_types import GUID


MINTAX_BUSINESS_TRAVELLERS_ID = UUID('39082041-08f3-44ec-a692-c637f55ecdbf')


class Application(db.Model):
    """Application model class"""
    __tablename__ = 'applications'

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    name = Column(String)
