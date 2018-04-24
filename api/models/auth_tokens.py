"""AuthToken model related functions"""

from datetime import datetime
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .storage import db
from .custom_types import GUID
from .users import User


class AuthToken(db.Model):
    """AuthToken model class"""
    __tablename__ = 'auth_tokens'

    # pylint: disable=C0103
    def __init__(self, pk, user):
        self.id = pk
        self.user = user

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)

    user_id = Column(GUID, ForeignKey('users.id'), nullable=False)
    user = relationship(User)

    issued_at = Column(DateTime, nullable=False, default=datetime.now)
    last_heartbeat = Column(DateTime, nullable=False, default=datetime.now)
