"""Track the processing of employee spreadsheet uploads"""

from sqlalchemy import Column, Boolean, DateTime, String
from .storage import db
from .custom_types import GUID


class EmployeeSpreadsheet(db.Model):
    """EmployeeSpreadsheet model class"""
    __tablename__ = 'employee_spreadsheets'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, upload_date,
                 active, file_name, upload_key):
        self.id = pk
        self.customer_id = customer_id
        self.upload_date = upload_date
        self.active = active
        self.file_name = file_name
        self.upload_key = upload_key

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    customer_id = Column(GUID)
    upload_date = Column(DateTime)
    active = Column(Boolean)
    file_name = Column(String)
    upload_key = Column(GUID)
