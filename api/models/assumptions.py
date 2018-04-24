"""Single per-user record table containing assumptions preferences"""

from sqlalchemy import Column, Boolean, String, Integer
from .storage import db
from .custom_types import GUID


class Assumptions(db.Model):
    """Assumptions model class"""
    __tablename__ = 'assumptions'

    def __init__(self, customer_id, outbound_uk_without_inbound,
                 business_trav_treaty_3159, business_trav_treaty_60183,
                 use_demin_incidental_workdays, deminimus_incidental_workdays,
                 use_demin_eeaa1_workdays, deminimus_eeaa1_workdays,
                 inbound_uk_without_outbound):
        self.customer_id = customer_id
        self.outbound_uk_without_inbound = outbound_uk_without_inbound
        self.business_trav_treaty_3159 = business_trav_treaty_3159
        self.business_trav_treaty_60183 = business_trav_treaty_60183
        self.use_demin_incidental_workdays = use_demin_incidental_workdays
        self.deminimus_incidental_workdays = deminimus_incidental_workdays
        self.use_demin_eeaa1_workdays = use_demin_eeaa1_workdays
        self.deminimus_eeaa1_workdays = deminimus_eeaa1_workdays
        self.inbound_uk_without_outbound = inbound_uk_without_outbound

    customer_id = Column(GUID, primary_key=True)
    outbound_uk_without_inbound = Column(String(1), nullable=False)
    business_trav_treaty_3159 = Column(String(1), nullable=False)
    business_trav_treaty_60183 = Column(String(1), nullable=False)
    use_demin_incidental_workdays = Column(Boolean, nullable=False)
    use_demin_eeaa1_workdays = Column(Boolean, nullable=False)
    deminimus_incidental_workdays = Column(Integer, nullable=True)
    deminimus_eeaa1_workdays = Column(Integer, nullable=True)
    inbound_uk_without_outbound = Column(String(1), nullable=False)
