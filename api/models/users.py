"""User model related functions"""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .storage import db
from .custom_types import GUID
from .customers import Customer


class User(db.Model):
    """User model class"""
    __tablename__ = 'users'

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    email = Column(String)
    password = Column(String)
    firstname = Column(String)
    secondname = Column(String)
    admin = Column(Boolean)
    active = Column(Boolean)
    unsucessful_login_attemps = Column(Integer)
    customer_id = Column(GUID, ForeignKey('customers.id'))
    customer = relationship(Customer, lazy='joined')
