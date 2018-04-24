# pylint: disable=C0111,W0611
"""Raw employees data processing test suite"""

from datetime import date
from models.employee_spreadsheets import EmployeeSpreadsheet
from models.employees import Employee, EmployeeArrangement
from .employees import process


# pylint: disable=C0103
def create_employee(pk=None, name='', employee_id='', arrangements=None):
    employee_spreadsheet_id = None
    return Employee(pk, employee_spreadsheet_id, name, employee_id, arrangements or [])


# pylint: disable=C0103
def create_arrangement(pk=None, employee_id='', category='1',
                       effective_from=None, effective_to=None):
    return EmployeeArrangement(pk, employee_id, category, effective_from, effective_to)


def test_empty_list():
    raw_data = []
    obtained = process(raw_data)
    expected = []
    assert obtained == expected


def test_single_valid_employee():
    john = create_employee(name='John', employee_id='123')
    raw_data = [john]
    obtained = process(raw_data)
    expected = [john]
    assert obtained == expected


def test_duplicate_employee_id():
    john = create_employee(name='John', employee_id='123')
    maria = create_employee(name='Maria', employee_id='123')
    miguel = create_employee(name='Miguel', employee_id='234')
    raw_data = [john, maria, miguel]
    obtained = process(raw_data)
    expected = [miguel]
    assert obtained == expected


def test_duplicate_employee_id_with_name():
    john = create_employee(name='John', employee_id=None)
    maria = create_employee(name='Maria', employee_id='John')
    raw_data = [john, maria]
    obtained = process(raw_data)
    expected = []
    assert obtained == expected


def test_multiple_empty_id():
    john = create_employee(name='John', employee_id=None)
    maria = create_employee(name='Maria', employee_id=None)
    miguel = create_employee(name='Miguel', employee_id='')
    alice = create_employee(name='Alice', employee_id='')
    raw_data = [john, maria, miguel, alice]
    obtained = process(raw_data)
    expected = [john, maria, miguel, alice]
    assert obtained == expected


def test_invalid_work_arrangements():
    arrangements = [
        create_arrangement(category=1, effective_from=None, effective_to=None),
        create_arrangement(category=2, effective_from=None, effective_to=None),
    ]
    john = create_employee(name='John', employee_id='123', arrangements=arrangements)
    raw_data = [john]
    obtained = process(raw_data)
    expected = []
    assert obtained == expected


def test_valid_work_arrangements():
    arrangements = [
        create_arrangement(category=1,
                           effective_from=date(2017, 1, 31), effective_to=date(2017, 2, 1)),
        create_arrangement(category=2,
                           effective_from=date(2017, 2, 2), effective_to=None),
    ]
    john = create_employee(name='John', employee_id='123', arrangements=arrangements)
    raw_data = [john]
    obtained = process(raw_data)
    expected = [john]
    assert obtained == expected


def test_valid_but_out_of_order_work_arrangements():
    arrangements = [
        create_arrangement(category=2,
                           effective_from=date(2017, 2, 2), effective_to=None),
        create_arrangement(category=1,
                           effective_from=date(2017, 1, 31), effective_to=date(2017, 2, 1)),
    ]
    john = create_employee(name='John', employee_id='123', arrangements=arrangements)
    raw_data = [john]
    obtained = process(raw_data)
    expected = [john]
    assert obtained == expected
