# pylint: disable=C0111,W0611,C0103
"""Report results processing test suite"""

from datetime import date, datetime
from .report_results import process


TRAVEL_HISTORY_UK_EMPLOYEE = '1'
TRAVEL_HISTORY_UNKNOWN = '2'
TRAVEL_HISTORY_TREATY_COUNTRY = '3'
TRAVEL_HISTORY_NON_TREATY_COUNTRY = '4'
TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR = '5'


def all_categories():
    return [TRAVEL_HISTORY_UK_EMPLOYEE,
            TRAVEL_HISTORY_UNKNOWN,
            TRAVEL_HISTORY_TREATY_COUNTRY,
            TRAVEL_HISTORY_NON_TREATY_COUNTRY,
            TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR]


def test_empty_input():
    employee_travel_history = []
    from_date = datetime(2017, 9, 1)
    to_date = datetime(2017, 9, 30)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = []
    assert obtained == expected


def test_single_stay_inside_period():
    employee_travel_history = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False}
    ]
    from_date = date(2017, 9, 1)
    to_date = date(2017, 9, 30)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1', 'stays': [
            {'category': TRAVEL_HISTORY_UK_EMPLOYEE, 'days': 21}
        ]}
    ]
    assert obtained == expected


def test_stay_overlapping_period_start():
    employee_travel_history = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False}
    ]
    from_date = date(2017, 9, 20)
    to_date = date(2017, 9, 30)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1', 'stays': [
            {'category': TRAVEL_HISTORY_UK_EMPLOYEE, 'days': 11}
        ]}
    ]
    assert obtained == expected


def test_stay_overlapping_period_end():
    employee_travel_history = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False}
    ]
    from_date = date(2017, 9, 1)
    to_date = date(2017, 9, 15)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1', 'stays': [
            {'category': TRAVEL_HISTORY_UK_EMPLOYEE, 'days': 6}
        ]}
    ]
    assert obtained == expected


def test_different_categories():
    employee_travel_history = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': datetime(2017, 9, 15, 13, 0),
         'originally_unclear': False},
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 17, 8, 0), 'to_date': None,
         'originally_unclear': False}
    ]
    from_date = date(2017, 9, 1)
    to_date = date(2017, 9, 30)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1', 'stays': [
            {'category': TRAVEL_HISTORY_UK_EMPLOYEE, 'days': 6},
            {'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY, 'days': 14},
        ]}
    ]
    assert obtained == expected


def test_multiple_stays_same_category():
    employee_travel_history = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': datetime(2017, 9, 15, 13, 0),
         'originally_unclear': False},
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 17, 8, 0), 'to_date': None,
         'originally_unclear': False}
    ]
    from_date = date(2017, 9, 1)
    to_date = date(2017, 9, 30)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1', 'stays': [
            {'category': TRAVEL_HISTORY_UK_EMPLOYEE, 'days': 20},
        ]}
    ]
    assert obtained == expected


def test_one_day_period():
    employee_travel_history = [
        {'traveller_name': 'SONIN/JOANNE/F', 'employee_id': '1610948',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2016, 4, 6, 0, 0), 'to_date': datetime(2016, 4, 6, 8, 35),
         'originally_unclear': False},
        {'traveller_name': 'SONIN/JOANNE/F', 'employee_id': '1610948',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2016, 4, 6, 16, 25), 'to_date': datetime(2016, 4, 12, 15, 25),
         'originally_unclear': False},
        {'traveller_name': 'SONIN/JOANNE/F', 'employee_id': '1610948',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2016, 4, 18, 20, 5), 'to_date': datetime(2016, 4, 19, 17, 10),
         'originally_unclear': False},
        {'traveller_name': 'SONIN/JOANNE/F', 'employee_id': '1610948',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2016, 4, 20, 17, 25), 'to_date': None,
         'originally_unclear': False},
    ]
    from_date = date(2017, 9, 11)
    to_date = date(2017, 9, 12)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'SONIN/JOANNE/F', 'employee_id': '1610948', 'stays': [
            {'category': TRAVEL_HISTORY_UK_EMPLOYEE, 'days': 2},
        ]},
    ]
    assert obtained == expected


def test_outside_report_period():
    employee_travel_history = [
        {'traveller_name': 'WILSON IV/THOMAS RIGGS', 'employee_id': '1021950',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2016, 4, 6, 0, 0), 'to_date': datetime(2016, 4, 7, 11, 0),
         'originally_unclear': True},
    ]
    from_date = date(2017, 9, 11)
    to_date = date(2017, 9, 12)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = []
    assert obtained == expected


def test_matching_end_of_period():
    employee_travel_history = [
        {'traveller_name': 'YILMAZ/ERALCIHAN', 'employee_id': '1317241',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2016, 4, 2, 11, 35), 'to_date': datetime(2016, 4, 5, 22, 15),
         'originally_unclear': False},
    ]
    from_date = date(2016, 3, 6)
    to_date = date(2016, 4, 5)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'YILMAZ/ERALCIHAN', 'employee_id': '1317241', 'stays': [
            {'category': TRAVEL_HISTORY_TREATY_COUNTRY, 'days': 4},
        ]}
    ]
    assert obtained == expected


def test_single_day_stay():
    employee_travel_history = [
        {'traveller_name': 'ANDERSON/CHARLES R', 'employee_id': '360418',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2016, 4, 1, 13, 5), 'to_date': datetime(2016, 4, 1, 16, 40),
         'originally_unclear': False},
    ]
    from_date = date(2016, 3, 6)
    to_date = date(2016, 4, 5)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'ANDERSON/CHARLES R', 'employee_id': '360418', 'stays': [
            {'category': TRAVEL_HISTORY_TREATY_COUNTRY, 'days': 1},
        ]}
    ]
    assert obtained == expected


def test_multiple_employees():
    employee_travel_history = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 15, 15, 0), 'to_date': datetime(2017, 9, 16, 13, 0),
         'originally_unclear': False},
    ]
    from_date = date(2017, 9, 1)
    to_date = date(2017, 9, 30)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1', 'stays': [
            {'category': TRAVEL_HISTORY_UK_EMPLOYEE, 'days': 21}
        ]},
        {'traveller_name': 'Maria', 'employee_id': '2', 'stays': [
            {'category': TRAVEL_HISTORY_TREATY_COUNTRY, 'days': 2}
        ]}
    ]
    assert obtained == expected


def test_multiple_periods_same_employee():
    employee_travel_history = [
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 15, 15, 0), 'to_date': datetime(2017, 9, 16, 13, 0),
         'originally_unclear': False},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 28, 11, 0), 'to_date': None,
         'originally_unclear': False},
    ]
    from_date = date(2017, 9, 1)
    to_date = date(2017, 9, 30)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': '2', 'stays': [
            {'category': TRAVEL_HISTORY_TREATY_COUNTRY, 'days': 5}
        ]},
    ]
    assert obtained == expected


def test_category_subset():
    employee_travel_history = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 15, 15, 0), 'to_date': datetime(2017, 9, 16, 13, 0),
         'originally_unclear': False},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 15, 15, 0), 'to_date': datetime(2017, 9, 16, 13, 0),
         'originally_unclear': False},
        {'traveller_name': 'Miguel', 'employee_id': '3',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 15, 15, 0), 'to_date': datetime(2017, 9, 16, 13, 0),
         'originally_unclear': False},
    ]
    from_date = date(2017, 9, 1)
    to_date = date(2017, 9, 30)
    categories = [TRAVEL_HISTORY_TREATY_COUNTRY, TRAVEL_HISTORY_NON_TREATY_COUNTRY]
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1', 'stays': [
            {'category': TRAVEL_HISTORY_TREATY_COUNTRY, 'days': 2}
        ]},
        {'traveller_name': 'Maria', 'employee_id': '2', 'stays': [
            {'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY, 'days': 2}
        ]},
    ]
    assert obtained == expected


def test_requested_to_date_before_from():
    employee_travel_history = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False}
    ]
    from_date = date(2017, 9, 30)
    to_date = date(2017, 9, 15)
    categories = all_categories()
    obtained = process(employee_travel_history, from_date, to_date, categories)
    expected = []
    assert obtained == expected
