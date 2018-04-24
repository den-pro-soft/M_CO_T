"""Information about Employees"""

from datetime import date
from itertools import groupby
from sqlalchemy import Column, String, Integer, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
from .storage import db
from .custom_types import GUID
from .employee_spreadsheets import EmployeeSpreadsheet


class Employee(db.Model):
    """Employee model class"""
    __tablename__ = 'employees'

    # pylint: disable=C0103
    def __init__(self, pk, employee_spreadsheet_id, name, employee_id, arrangements):
        self.id = pk
        self.employee_spreadsheet_id = employee_spreadsheet_id
        self.name = name
        self.employee_id = employee_id
        self.arrangements = arrangements

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    employee_spreadsheet_id = Column(GUID, ForeignKey('employee_spreadsheets.id'))
    employee_spreadsheet = relationship(EmployeeSpreadsheet,
                                        backref=backref('employees',
                                                        lazy='raise',
                                                        cascade='all, delete-orphan'))
    name = Column(String)
    employee_id = Column(String)

    @property
    def effective_id(self):
        """Returns the effective employee ID, i.e. their ID or their name if ID is blank"""
        return self.employee_id if self.employee_id else self.name

    def valid_work_arrangements(self):
        """Returns true if the employees arrangements are in a valid state"""
        arrangements = list(map(lambda arr: {
            "effectiveFrom": arr.effective_from,
            "effectiveTo": arr.effective_to,
        }, self.sorted_arrangements()))
        return not EmployeeArrangement.has_duplication(arrangements)

    def sorted_arrangements(self):
        """Returns a list of arrangements sorted by effective period"""
        return sorted(self.arrangements,
                      key=lambda x: (x.effective_from or date(9999, 1, 1),
                                     x.effective_to or date(9999, 1, 1)))

    @classmethod
    def duplicated_ids(cls, employees):
        """Checks for duplicated employee ID"""
        employee_ids = sorted([emp.employee_id if emp.employee_id else emp.name \
                               for emp in employees])
        return [employee_id for employee_id, group in groupby(employee_ids) if len(list(group)) > 1]


class EmployeeArrangement(db.Model):
    """EmployeeArrangement model class"""
    __tablename__ = 'employee_arrangements'

    # pylint: disable=C0103
    def __init__(self, pk, employee_id, category, effective_from, effective_to):
        self.id = pk
        self.employee_id = employee_id
        self.category = category
        self.effective_from = effective_from
        self.effective_to = effective_to

    id = Column(GUID, primary_key=True)
    employee_id = Column(GUID, ForeignKey('employees.id'))
    employee = relationship(Employee, backref=backref('arrangements',
                                                      lazy='raise',
                                                      cascade='all, delete-orphan'))
    category = Column(Integer)
    effective_from = Column(Date)
    effective_to = Column(Date)

    @classmethod
    def has_duplication(cls, arrangements):
        """Checks if the arrangement dicts {effectiveFrom, effectiveTo} are valid"""
        if len(arrangements) > 1:
            for idx, arr in enumerate(arrangements):
                empty_from = not arr['effectiveFrom']
                not_last_and_empty_to = (idx + 1) != len(arrangements) and not arr['effectiveTo']
                if empty_from or not_last_and_empty_to:
                    return True
            return False


class HomeCountryClarification(db.Model):
    """HomeCountryClarification model class"""
    __tablename__ = 'home_country_clarifications'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, effective_employee_id,
                 home_country, from_date, to_date):
        self.id = pk
        self.customer_id = customer_id
        self.effective_employee_id = effective_employee_id
        self.home_country = home_country
        self.from_date = from_date
        self.to_date = to_date

    id = Column(GUID, primary_key=True)
    customer_id = Column(GUID)
    effective_employee_id = Column(String)
    home_country = Column(String)
    from_date = Column(DateTime)
    to_date = Column(DateTime)


class InboundAssumptionConfirmation(db.Model):
    """InboundAssumptionConfirmation model class"""
    __tablename__ = 'inbound_assumption_confirmations'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, effective_employee_id,
                 to_date, confirmed, correct_date):
        self.id = pk
        self.customer_id = customer_id
        self.effective_employee_id = effective_employee_id
        self.to_date = to_date
        self.confirmed = confirmed
        self.correct_date = correct_date

    id = Column(GUID, primary_key=True)
    customer_id = Column(GUID)
    effective_employee_id = Column(String)
    to_date = Column(DateTime)
    confirmed = Column(Boolean)
    correct_date = Column(DateTime)


class OutboundAssumptionConfirmation(db.Model):
    """OutboundAssumptionConfirmation model class"""
    __tablename__ = 'outbound_assumption_confirmations'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, effective_employee_id,
                 from_date, confirmed, correct_date):
        self.id = pk
        self.customer_id = customer_id
        self.effective_employee_id = effective_employee_id
        self.from_date = from_date
        self.confirmed = confirmed
        self.correct_date = correct_date

    id = Column(GUID, primary_key=True)
    customer_id = Column(GUID)
    effective_employee_id = Column(String)
    from_date = Column(DateTime)
    confirmed = Column(Boolean)
    correct_date = Column(DateTime)


class BorderCrossTimeClarification(db.Model):
    """BorderCrossTimeClarification model class"""
    __tablename__ = 'border_cross_time_clarifications'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, employee_name,
                 employee_id, border_cross, origin_country,
                 destination_country, correct_time):
        self.id = pk
        self.customer_id = customer_id
        self.employee_name = employee_name
        self.employee_id = employee_id
        self.border_cross = border_cross
        self.origin_country = origin_country
        self.destination_country = destination_country
        self.correct_time = correct_time

    id = Column(GUID, primary_key=True)
    customer_id = Column(GUID)
    employee_name = Column(String)
    employee_id = Column(String)
    border_cross = Column(DateTime)
    origin_country = Column(String)
    destination_country = Column(String)
    correct_time = Column(DateTime)


class SamePersonConfirmation(db.Model):
    """SamePersonConfirmation model class"""
    __tablename__ = 'same_person_confirmations'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, effective_employee_id):
        self.id = pk
        self.customer_id = customer_id
        self.effective_employee_id = effective_employee_id

    id = Column(GUID, primary_key=True)
    customer_id = Column(GUID)
    effective_employee_id = Column(String)
