# pylint: disable=C0111,W0611
"""Employee travel history processing test suite"""

from datetime import date, time, datetime
from models.traveller_data import TravellerData
from models.travels import Travel
from models.employee_spreadsheets import EmployeeSpreadsheet
from models.employees import Employee, EmployeeArrangement, \
                             HomeCountryClarification, InboundAssumptionConfirmation, \
                             OutboundAssumptionConfirmation
from models.treaties import Treaty
from models.assumptions import Assumptions
from .employee_travel_history import process


TRAVEL_HISTORY_UK_EMPLOYEE = 1
TRAVEL_HISTORY_UNKNOWN = 2
TRAVEL_HISTORY_TREATY_COUNTRY = 3
TRAVEL_HISTORY_NON_TREATY_COUNTRY = 4
TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR = 5
TRAVEL_HISTORY_UK_EXPATRIATE = 6

WORK_ARRANGEMENT_UK_EMPLOYEE = 1
WORK_ARRANGEMENT_OVERSEAS_BRANCH = 2
WORK_ARRANGEMENT_UK_EXPATRIATE = 3
WORK_ARRANGEMENT_NT_STA = 4

ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR = '1'
ASSUMPTION_OUT_WITHOUT_IN_TAX_MONTH = '2'
ASSUMPTION_OUT_WITHOUT_IN_SAME_DAY = '3'

ASSUMPTION_IN_WITHOUT_OUT_TRY_NON_CROSSING = '1'
ASSUMPTION_IN_WITHOUT_OUT_TAX_YEAR_END = '2'


# pylint: disable=C0103
def create_employee(pk=None, name='', employee_id='', arrangements=None):
    employee_spreadsheet_id = None
    return Employee(pk, employee_spreadsheet_id, name, employee_id, arrangements or [])


# pylint: disable=C0103
def create_arrangement(pk=None, employee_id='', category='1',
                       effective_from=None, effective_to=None):
    return EmployeeArrangement(pk, employee_id, category, effective_from, effective_to)


# pylint: disable=C0103
def create_clarification(name, employee_id, home_country, from_date, to_date):
    pk = None
    customer_id = None
    effective_employee_id = employee_id if employee_id else name
    return HomeCountryClarification(pk, customer_id, effective_employee_id,
                                    home_country, from_date, to_date)


def create_inbound_assumption_confirmation(name, employee_id, to_date, correct_date):
    pk = None
    customer_id = None
    effective_employee_id = employee_id if employee_id else name
    return InboundAssumptionConfirmation(pk, customer_id, effective_employee_id,
                                         to_date, False, correct_date)


def create_outbound_assumption_confirmation(name, employee_id, from_date, correct_date):
    pk = None
    customer_id = None
    effective_employee_id = employee_id if employee_id else name
    return OutboundAssumptionConfirmation(pk, customer_id, effective_employee_id,
                                          from_date, False, correct_date)


# pylint: disable=C0103
def create_treaty(country, from_date, to_date):
    pk = None
    return Treaty(pk, country, from_date, to_date)


# pylint: disable=C0103
def create_assumption(outbound_uk_without_inbound,
                      inbound_uk_without_outbound=ASSUMPTION_IN_WITHOUT_OUT_TRY_NON_CROSSING):
    return Assumptions(customer_id=None, outbound_uk_without_inbound=outbound_uk_without_inbound,
                       business_trav_treaty_3159=None, business_trav_treaty_60183=None,
                       use_demin_incidental_workdays=False, deminimus_incidental_workdays=None,
                       use_demin_eeaa1_workdays=False, deminimus_eeaa1_workdays=None,
                       inbound_uk_without_outbound=inbound_uk_without_outbound)


# pylint: disable=C0103,R0914
def create_trip(traveller_name, employee_id, employee_country,
                origin, destination,
                departure_date, departure_time,
                arrival_date, arrival_time,
                ticket_type='Straight Ticket', invalid=False, pk=None):
    traveller_data_id = None
    employing_entity = None
    au = None
    booking_date = None
    record_locator = None
    ticket_no = None
    segment_no = None
    calculated_seg_no = None
    origin_airport_code = None
    destination_airport_code = None
    routing_airports = None
    row = 0
    border_cross = datetime.combine(departure_date, departure_time) if destination != 'GBR' else \
                   datetime.combine(arrival_date, arrival_time) if destination == 'GBR' else None
    return Travel(pk, traveller_data_id, traveller_name, employee_id,
                  employing_entity, employee_country, au, booking_date,
                  record_locator, ticket_no, ticket_type, segment_no,
                  calculated_seg_no, origin, origin_airport_code,
                  destination, destination_airport_code,
                  routing_airports, departure_date, departure_time,
                  arrival_date, arrival_time, invalid, row, border_cross)

def test_empty_input():
    employees = []
    trips = []
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = []
    assert obtained == expected


def test_uk_employee():
    employees = []
    trips = [
        create_trip('John', '1', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_unknown_home_country():
    employees = []
    trips = [
        create_trip('Maria', '2', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_uk_employee_via_spreadsheet():
    employees = [
        create_employee(name='Marcus', employee_id='3', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE)
        ])
    ]
    trips = [
        create_trip('Marcus', '3', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Marcus', 'employee_id': '3',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_discrepancy_between_employee_country_and_employee_spreadsheet():
    employees = [
        create_employee(name='Julia', employee_id='4', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE)
        ])
    ]
    trips = [
        create_trip('Julia', '4', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Julia', 'employee_id': '4',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_unknown_home_country_clarified_as_GBR():
    employees = []
    trips = [
        create_trip('Michael', '5', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Michael', '5', 'GBR',
                             datetime(2017, 9, 10, 11, 0), None)
    ]
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Michael', 'employee_id': '5',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_unknown_home_country_clarified_as_treaty():
    employees = []
    trips = [
        create_trip('Paul', '6', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Paul', '6', 'ITA',
                             datetime(2017, 9, 10, 11, 0), None)
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2017, 9, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Paul', 'employee_id': '6',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_unknown_home_country_clarified_as_non_treaty():
    employees = []
    trips = [
        create_trip('Beth', '7', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Beth', '7', 'BRA',
                             datetime(2017, 9, 10, 11, 0), None)
    ]
    assumptions = None
    treaties = [
        create_treaty('BRA', date(2017, 8, 1), date(2017, 8, 31)),
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Beth', 'employee_id': '7',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_clarified_discrepancy_between_employees_and_trips_as_GBR():
    employees = [
        create_employee(name='Carlos', employee_id='8', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE)
        ])
    ]
    trips = [
        create_trip('Carlos', '8', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Carlos', '8', 'GBR',
                             datetime(2017, 9, 10, 11, 0), None)
    ]
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Carlos', 'employee_id': '8',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_clarified_discrepancy_between_employees_and_trips_as_treaty():
    employees = [
        create_employee(name='Joseph', employee_id='9', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE)
        ])
    ]
    trips = [
        create_trip('Joseph', '9', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Joseph', '9', 'ITA',
                             datetime(2017, 9, 10, 11, 0), None)
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2017, 9, 1), date(2017, 9, 10))
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Joseph', 'employee_id': '9',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_uk_expatriate_empty_home_country():
    employees = [
        create_employee(name='Lucia', employee_id='10', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE)
        ])
    ]
    trips = [
        create_trip('Lucia', '10', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Lucia', 'employee_id': '10',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_uk_expatriate_GBR_home_country():
    employees = [
        create_employee(name='Kyle', employee_id='11', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE)
        ])
    ]
    trips = [
        create_trip('Kyle', '11', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Kyle', 'employee_id': '11',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_uk_expatriate_ITA_home_country():
    employees = [
        create_employee(name='Link', employee_id='12', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE)
        ])
    ]
    trips = [
        create_trip('Link', '12', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Link', 'employee_id': '12',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_overseas_visitor_empty_home_country():
    employees = [
        create_employee(name='Victor', employee_id='13', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH)
        ])
    ]
    trips = [
        create_trip('Victor', '13', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Victor', 'employee_id': '13',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_overseas_visitor_GBR_home_country():
    employees = [
        create_employee(name='Trevor', employee_id='14', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH)
        ])
    ]
    trips = [
        create_trip('Trevor', '14', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Trevor', 'employee_id': '14',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_overseas_visitor_ITA_home_country():
    employees = [
        create_employee(name='Cecilia', employee_id='15', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH)
        ])
    ]
    trips = [
        create_trip('Cecilia', '15', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Cecilia', 'employee_id': '15',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_treaty_country_visitor():
    employees = []
    trips = [
        create_trip('Kelly', '16', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2017, 9, 10), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Kelly', 'employee_id': '16',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_non_treaty_country_visitor():
    employees = []
    trips = [
        create_trip('Oliver', '17', 'BRA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2017, 9, 10), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Oliver', 'employee_id': '17',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_nt_sta_from_GBR_clarified_as_non_treaty():
    employees = [
        create_employee(name='Philip', employee_id='18', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA)
        ])
    ]
    trips = [
        create_trip('Philip', '18', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Philip', '18', 'BRA',
                             datetime(2017, 9, 10, 11, 0), None)
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2017, 9, 10), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Philip', 'employee_id': '18',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_nt_sta_from_GBR_clarified_as_treaty():
    employees = [
        create_employee(name='David', employee_id='19', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA)
        ])
    ]
    trips = [
        create_trip('David', '19', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('David', '19', 'ITA',
                             datetime(2017, 9, 10, 11, 0), None)
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2017, 9, 10), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'David', 'employee_id': '19',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_nt_sta_from_GBR_clarified_as_GBR():
    employees = [
        create_employee(name='Debora', employee_id='20', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA)
        ])
    ]
    trips = [
        create_trip('Debora', '20', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Debora', '20', 'GBR',
                             datetime(2017, 9, 10, 11, 0), None)
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2017, 9, 10), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Debora', 'employee_id': '20',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_nt_sta_from_GBR_still_unanswered():
    employees = [
        create_employee(name='Jack', employee_id='21', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA)
        ])
    ]
    trips = [
        create_trip('Jack', '21', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2017, 9, 10), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Jack', 'employee_id': '21',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_nt_sta_from_non_treaty():
    employees = [
        create_employee(name='Livia', employee_id='22', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA)
        ])
    ]
    trips = [
        create_trip('Livia', '22', 'BRA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2017, 9, 10), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Livia', 'employee_id': '22',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_nt_sta_from_treaty():
    employees = [
        create_employee(name='Sergio', employee_id='23', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA)
        ])
    ]
    trips = [
        create_trip('Sergio', '23', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2017, 9, 10), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Sergio', 'employee_id': '23',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_outbound_without_in_with_tax_year_assumption():
    employees = []
    trips = [
        create_trip('Richard', '24', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Richard', 'employee_id': '24',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 4, 6, 0, 0), 'to_date': datetime(2017, 9, 10, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': True,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_outbound_without_in_with_tax_month_assumption():
    employees = []
    trips = [
        create_trip('Zach', '25', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_MONTH)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Zach', 'employee_id': '25',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 6, 0, 0), 'to_date': datetime(2017, 9, 10, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': True,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_outbound_without_in_with_same_day_assumption():
    employees = []
    trips = [
        create_trip('Rodolph', '26', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_SAME_DAY)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Rodolph', 'employee_id': '26',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 10, 0), 'to_date': datetime(2017, 9, 10, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': True,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_inbound_plus_outbound():
    employees = []
    trips = [
        create_trip('Bob', '28', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0)),
        create_trip('Bob', '28', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 15), time(10, 0),
                    date(2017, 9, 15), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Bob', 'employee_id': '28',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': datetime(2017, 9, 15, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_different_departure_arrival_dates():
    employees = []
    trips = [
        create_trip('Willian', '29', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 11), time(11, 0)),
        create_trip('Willian', '29', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 14), time(10, 0),
                    date(2017, 9, 15), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Willian', 'employee_id': '29',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 11, 0), 'to_date': datetime(2017, 9, 14, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_multiple_periods_in_uk():
    employees = []
    trips = [
        create_trip('Igor', '32', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0)),
        create_trip('Igor', '32', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 12), time(10, 0),
                    date(2017, 9, 12), time(11, 0)),
        create_trip('Igor', '32', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0)),
        create_trip('Igor', '32', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 20), time(10, 0),
                    date(2017, 9, 20), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Igor', 'employee_id': '32',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': datetime(2017, 9, 12, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Igor', 'employee_id': '32',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_two_subsequent_outbound_flights():
    employees = []
    trips = [
        create_trip('Yuri', '34', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0)),
        create_trip('Yuri', '34', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 17), time(10, 0),
                    date(2017, 9, 17), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Yuri', 'employee_id': '34',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 4, 6, 0, 0), 'to_date': datetime(2017, 9, 17, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': True,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_two_subsequent_inbound_flights():
    employees = []
    trips = [
        create_trip('Francis', '35', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0)),
        create_trip('Francis', '35', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 17), time(10, 0),
                    date(2017, 9, 17), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Francis', 'employee_id': '35',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_overlapping_impossible_flights():
    employees = []
    trips = [
        create_trip('Douglas', '36', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 17), time(10, 0),
                    date(2017, 9, 17), time(11, 0)),
        create_trip('Douglas', '36', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 17), time(10, 30),
                    date(2017, 9, 17), time(11, 30)),
        create_trip('Douglas', '36', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 19), time(10, 0),
                    date(2017, 9, 19), time(11, 0)),
        create_trip('Douglas', '36', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 19), time(10, 30),
                    date(2017, 9, 19), time(11, 30))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Douglas', 'employee_id': '36',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 4, 6, 0, 0), 'to_date': datetime(2017, 9, 17, 10, 30),
         'originally_unclear': False, 'originally_assumed_inbound': True,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Douglas', 'employee_id': '36',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 17, 11, 0), 'to_date': datetime(2017, 9, 19, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Douglas', 'employee_id': '36',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 19, 11, 30), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_sudden_change_employee_country():
    employees = []
    trips = [
        create_trip('Travis', '37', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0)),
        create_trip('Travis', '37', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 20), time(10, 0),
                    date(2017, 9, 20), time(11, 0)),
        create_trip('Travis', '37', 'BRA', 'BRA', 'GBR',
                    date(2017, 9, 25), time(10, 0),
                    date(2017, 9, 25), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Travis', 'employee_id': '37',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Travis', 'employee_id': '37',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 25, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_uk_emp_overseas():
    employees = [
        create_employee(name='Tulio', employee_id='38', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Tulio', '38', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Tulio', 'employee_id': '38',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Tulio', 'employee_id': '38',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_uk_emp_nt_sta():
    employees = [
        create_employee(name='Sulivan', employee_id='39', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Sulivan', '39', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Sulivan', '39', 'ITA',
                             datetime(2017, 9, 21), None)
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Sulivan', 'employee_id': '39',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Sulivan', 'employee_id': '39',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_uk_emp_uk_expat():
    employees = [
        create_employee(name='Polyana', employee_id='40', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Polyana', '40', None, 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Polyana', 'employee_id': '40',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Polyana', 'employee_id': '40',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_uk_expat_uk_emp():
    employees = [
        create_employee(name='Helena', employee_id='41', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Helena', '41', None, 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Helena', 'employee_id': '41',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Helena', 'employee_id': '41',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_uk_expat_overseas():
    employees = [
        create_employee(name='Alexander', employee_id='42', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Alexander', '42', None, 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Alexander', 'employee_id': '42',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Alexander', 'employee_id': '42',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_uk_expat_nt_sta():
    employees = [
        create_employee(name='Jeremias', employee_id='43', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Jeremias', '43', 'BRA', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Jeremias', 'employee_id': '43',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Jeremias', 'employee_id': '43',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_overseas_uk_emp():
    employees = [
        create_employee(name='Valeria', employee_id='44', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Valeria', '44', 'BRA', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Valeria', '44', 'GBR',
                             datetime(2017, 9, 21), None)
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Valeria', 'employee_id': '44',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Valeria', 'employee_id': '44',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_overseas_uk_expat():
    employees = [
        create_employee(name='Donovan', employee_id='45', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Donovan', '45', 'BRA', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Donovan', 'employee_id': '45',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Donovan', 'employee_id': '45',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_overseas_nt_sta():
    employees = [
        create_employee(name='Wellington', employee_id='46', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Wellington', '46', None, 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Wellington', '46', 'BRA',
                             datetime(2017, 9, 21), None)
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Wellington', 'employee_id': '46',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Wellington', 'employee_id': '46',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_nt_sta_uk_emp():
    employees = [
        create_employee(name='Lucas', employee_id='47', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Lucas', '47', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Lucas', 'employee_id': '47',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Lucas', 'employee_id': '47',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_nt_sta_uk_expat():
    employees = [
        create_employee(name='Hilary', employee_id='48', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Hilary', '48', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Hilary', '48', 'ITA',
                             datetime(2017, 9, 16, 11, 0), datetime(2017, 9, 20, 23, 59, 59))
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Hilary', 'employee_id': '48',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Hilary', 'employee_id': '48',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_nt_sta_overseas():
    employees = [
        create_employee(name='Manuel', employee_id='49', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 20)),
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH,
                               effective_from=date(2017, 9, 21))
        ])
    ]
    trips = [
        create_trip('Manuel', '49', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 16), time(10, 0),
                    date(2017, 9, 16), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Manuel', 'employee_id': '49',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 16, 11, 0), 'to_date': datetime(2017, 9, 20, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Manuel', 'employee_id': '49',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_all_four():
    employees = [
        create_employee(name='Nathan', employee_id='50', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 7)),
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH,
                               effective_from=date(2017, 9, 8), effective_to=date(2017, 9, 9)),
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE,
                               effective_from=date(2017, 9, 10), effective_to=date(2017, 9, 11)),
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE,
                               effective_from=date(2017, 9, 12), effective_to=date(2017, 9, 13)),
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA,
                               effective_from=date(2017, 9, 14), effective_to=date(2017, 9, 15)),
            create_arrangement(category=WORK_ARRANGEMENT_OVERSEAS_BRANCH,
                               effective_from=date(2017, 9, 16))
        ])
    ]
    trips = [
        create_trip('Nathan', '50', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 5), time(10, 0),
                    date(2017, 9, 5), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Nathan', '50', 'BRA',
                             datetime(2017, 9, 5, 11, 0), datetime(2017, 9, 7, 23, 59, 59)),
        create_clarification('Nathan', '50', 'GBR',
                             datetime(2017, 9, 10, 0, 0), datetime(2017, 9, 11, 23, 59, 59)),
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Nathan', 'employee_id': '50',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 5, 11, 0), 'to_date': datetime(2017, 9, 7, 23, 59, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Nathan', 'employee_id': '50',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 8, 0, 0), 'to_date': datetime(2017, 9, 9, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Nathan', 'employee_id': '50',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 0, 0), 'to_date': datetime(2017, 9, 11, 23, 59, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Nathan', 'employee_id': '50',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 12, 0, 0), 'to_date': datetime(2017, 9, 13, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Nathan', 'employee_id': '50',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 14, 0, 0), 'to_date': datetime(2017, 9, 15, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Nathan', 'employee_id': '50',
         'category': TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR,
         'from_date': datetime(2017, 9, 16, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_multiple_arrangements_plus_sudden_country_change():
    employees = [
        create_employee(name='Victoria', employee_id='51', arrangements=[
            create_arrangement(category=WORK_ARRANGEMENT_UK_EMPLOYEE,
                               effective_from=date(2017, 1, 1), effective_to=date(2017, 9, 7)),
            create_arrangement(category=WORK_ARRANGEMENT_NT_STA,
                               effective_from=date(2017, 9, 8), effective_to=date(2017, 9, 15)),
            create_arrangement(category=WORK_ARRANGEMENT_UK_EXPATRIATE,
                               effective_from=date(2017, 9, 19))
        ])
    ]
    trips = [
        create_trip('Victoria', '51', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 5), time(10, 0),
                    date(2017, 9, 5), time(11, 0)),
        create_trip('Victoria', '51', 'GBR', 'GBR', 'BRA',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0)),
        create_trip('Victoria', '51', 'BRA', 'BRA', 'GBR',
                    date(2017, 9, 13), time(10, 0),
                    date(2017, 9, 13), time(11, 0)),
    ]
    home_country_clarifications = [
        create_clarification('Victoria', '51', 'ITA',
                             datetime(2017, 9, 8, 0, 0), datetime(2017, 9, 10, 10, 0, 0)),
    ]
    assumptions = None
    treaties = [
        create_treaty('ITA', date(2000, 1, 1), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Victoria', 'employee_id': '51',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 5, 11, 0), 'to_date': datetime(2017, 9, 7, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Victoria', 'employee_id': '51',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 8, 0, 0), 'to_date': datetime(2017, 9, 10, 10, 0, 0),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Victoria', 'employee_id': '51',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 13, 11, 0), 'to_date': datetime(2017, 9, 18, 23, 59, 59),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Victoria', 'employee_id': '51',
         'category': TRAVEL_HISTORY_UK_EXPATRIATE,
         'from_date': datetime(2017, 9, 19, 0, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_inbound_assumption_confirmation():
    employees = []
    trips = [
        create_trip('Richard', '24', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    inbound_assumption_confirmations = [
        create_inbound_assumption_confirmation('Richard', '24',
                                               datetime(2017, 9, 10, 10, 0),
                                               correct_date=datetime(2017, 4, 10))
    ]
    obtained = process(employees, trips, home_country_clarifications,
                       assumptions, treaties, inbound_assumption_confirmations)
    expected = [
        {'traveller_name': 'Richard', 'employee_id': '24',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 4, 10, 0, 0), 'to_date': datetime(2017, 9, 10, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': True,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_multiple_employee_home_country():
    employees = []
    trips = [
        create_trip('Jose', '26', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0)),
        create_trip('Jose', '26', 'BRA', 'GBR', 'ITA',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    inbound_assumption_confirmations = []
    obtained = process(employees, trips, home_country_clarifications,
                       assumptions, treaties, inbound_assumption_confirmations)
    expected = [
        {'traveller_name': 'Jose', 'employee_id': '26',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 4, 6, 0, 0), 'to_date': datetime(2017, 9, 10, 10, 0),
         'originally_unclear': True, 'originally_assumed_inbound': True,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_clarified_home_country_no_periods():
    employees = []
    trips = [
        create_trip('Maria', '2', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Maria', '2', 'BRA',
                             None, None)
    ]
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_clarified_home_country_inbound_only_no_intersection():
    employees = []
    trips = [
        create_trip('Maria', '2', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Maria', '2', 'BRA',
                             datetime(2017, 1, 1, 0, 0),
                             datetime(2017, 2, 2, 0, 0))
    ]
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_clarified_home_country_inbound_single_day_intersection():
    employees = []
    trips = [
        create_trip('Maria', '2', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Maria', '2', 'BRA',
                             datetime(2017, 1, 1, 0, 0),
                             datetime(2017, 9, 10, 23, 59))
    ]
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': datetime(2017, 9, 10, 23, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 11, 0, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_clarified_home_country_inbound_inner_intersection():
    employees = []
    trips = [
        create_trip('Maria', '2', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0))
    ]
    home_country_clarifications = [
        create_clarification('Maria', '2', 'BRA',
                             datetime(2017, 9, 15, 0, 0),
                             datetime(2017, 9, 20, 23, 59))
    ]
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': datetime(2017, 9, 14, 23, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 15, 0, 0), 'to_date': datetime(2017, 9, 20, 23, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 21, 0, 0), 'to_date': None,
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_clarified_home_country_full_stay_outer_intersection():
    employees = []
    trips = [
        create_trip('Maria', '2', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0)),
        create_trip('Maria', '2', None, 'GBR', 'ITA',
                    date(2017, 9, 15), time(12, 0),
                    date(2017, 9, 15), time(13, 0))
    ]
    home_country_clarifications = [
        create_clarification('Maria', '2', 'BRA',
                             datetime(2017, 9, 5, 0, 0),
                             datetime(2017, 9, 20, 23, 59))
    ]
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': datetime(2017, 9, 15, 12, 0),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_clarified_home_country_full_stay_no_intersection():
    employees = []
    trips = [
        create_trip('Maria', '2', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0)),
        create_trip('Maria', '2', None, 'GBR', 'ITA',
                    date(2017, 9, 15), time(12, 0),
                    date(2017, 9, 15), time(13, 0))
    ]
    home_country_clarifications = [
        create_clarification('Maria', '2', 'BRA',
                             datetime(2016, 9, 5, 0, 0),
                             datetime(2016, 9, 20, 23, 59))
    ]
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': datetime(2017, 9, 15, 12, 0),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_clarified_home_country_full_stay_inner_intersection():
    employees = []
    trips = [
        create_trip('Maria', '2', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0)),
        create_trip('Maria', '2', None, 'GBR', 'ITA',
                    date(2017, 9, 15), time(12, 0),
                    date(2017, 9, 15), time(13, 0))
    ]
    home_country_clarifications = [
        create_clarification('Maria', '2', 'BRA',
                             datetime(2017, 9, 12, 0, 0),
                             datetime(2017, 9, 13, 23, 59))
    ]
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': datetime(2017, 9, 11, 23, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 12, 0, 0), 'to_date': datetime(2017, 9, 13, 23, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 14, 0, 0), 'to_date': datetime(2017, 9, 15, 12, 0),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_clarified_home_country_full_stay_all_intersection_types():
    employees = []
    trips = [
        create_trip('Maria', '2', None, 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0)),
        create_trip('Maria', '2', None, 'GBR', 'ITA',
                    date(2017, 9, 15), time(12, 0),
                    date(2017, 9, 15), time(13, 0))
    ]
    home_country_clarifications = [
        create_clarification('Maria', '2', 'BRA',
                             datetime(2017, 9, 12, 0, 0),
                             datetime(2017, 9, 13, 23, 59)),
        create_clarification('Maria', '2', 'ITA',
                             datetime(2016, 9, 12, 0, 0),
                             datetime(2016, 9, 13, 23, 59)),
        create_clarification('Maria', '2', 'USA',
                             datetime(2017, 9, 15, 0, 0),
                             None)
    ]
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': datetime(2017, 9, 11, 23, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 12, 0, 0), 'to_date': datetime(2017, 9, 13, 23, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_UNKNOWN,
         'from_date': datetime(2017, 9, 14, 0, 0), 'to_date': datetime(2017, 9, 14, 23, 59),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Maria', 'employee_id': '2',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 15, 0, 0), 'to_date': datetime(2017, 9, 15, 12, 0),
         'originally_unclear': True, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
    ]
    assert obtained == expected


def test_outbound_trip_id_without_outbound_flight():
    employees = []
    trips = [
        create_trip('John', '1', 'GBR', 'ITA', 'GBR',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0), pk=123)
    ]
    home_country_clarifications = []
    assumptions = None
    treaties = []
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_UK_EMPLOYEE,
         'from_date': datetime(2017, 9, 10, 11, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': 123}
    ]
    assert obtained == expected


def test_outbound_trip_id_with_outbound_flight():
    employees = []
    trips = [
        create_trip('Richard', '24', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 10), time(10, 0),
                    date(2017, 9, 10), time(11, 0), pk=123)
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Richard', 'employee_id': '24',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 4, 6, 0, 0), 'to_date': datetime(2017, 9, 10, 10, 0),
         'originally_unclear': False, 'originally_assumed_inbound': True,
         'originally_assumed_outbound': False, 'outbound_trip_id': 123,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_single_day_stay_with_departure_date_one_off():
    employees = []
    trips = [
        create_trip('John', '1', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 10), time(0, 0),
                    date(2017, 9, 11), time(0, 0)),
        create_trip('John', '1', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(0, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 0, 0), 'to_date': datetime(2017, 9, 11, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_single_day_stay_with_arrival_date_one_off():
    employees = []
    trips = [
        create_trip('John', '1', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(0, 0)),
        create_trip('John', '1', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 12), time(0, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 0, 0), 'to_date': datetime(2017, 9, 11, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_single_day_stay_with_arrival_date_one_off_out_of_order():
    employees = []
    trips = [
        create_trip('John', '1', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 12), time(0, 0)),
        create_trip('John', '1', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(0, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 0, 0), 'to_date': datetime(2017, 9, 11, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_only_id_matters_when_grouping_trips():
    employees = []
    trips = [
        create_trip('John', '1', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 12), time(0, 0)),
        create_trip('Johny', '1', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(0, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'John', 'employee_id': '1',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 0, 0), 'to_date': datetime(2017, 9, 11, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_if_blank_employee_id_name_gets_used_instead():
    employees = []
    trips = [
        create_trip('Maria', 'John', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 12), time(0, 0)),
        create_trip('John', None, 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(0, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': 'John',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 0, 0), 'to_date': datetime(2017, 9, 11, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_first_non_empty_name_is_used_when_multiple_options():
    employees = []
    trips = [
        create_trip('', '1', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 12), time(0, 0)),
        create_trip('Johny', '1', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(0, 0))
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Johny', 'employee_id': '1',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 0, 0), 'to_date': datetime(2017, 9, 11, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_dont_use_name_as_id_in_output():
    employees = []
    trips = [
        create_trip('John', 'John', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 12), time(0, 0)),
        create_trip('John', 'John', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(0, 0)),
        create_trip('Maria', '', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 12), time(0, 0)),
        create_trip('Maria', '', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(0, 0)),
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'John', 'employee_id': 'John',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 0, 0), 'to_date': datetime(2017, 9, 11, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None},
        {'traveller_name': 'Maria', 'employee_id': '',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 0, 0), 'to_date': datetime(2017, 9, 11, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': None}
    ]
    assert obtained == expected


def test_use_next_outbound_irrespective_of_departure_country():
    employees = []
    trips = [
        create_trip('John', 'John', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(1, 0), pk=123),
        create_trip('John', 'John', 'ITA', 'BRA', 'ITA',
                    date(2017, 9, 13), time(0, 0),
                    date(2017, 9, 13), time(1, 0)),
        create_trip('John', 'John', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 15), time(0, 0),
                    date(2017, 9, 15), time(1, 0)),
        create_trip('Maria', 'Maria', 'ESP', 'ESP', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(1, 0), pk=234),
        create_trip('Maria', 'Maria', 'ESP', 'BRA', 'ESP',
                    date(2017, 9, 13), time(0, 0),
                    date(2017, 9, 13), time(1, 0)),
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'John', 'employee_id': 'John',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 1, 0), 'to_date': datetime(2017, 9, 15, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': 123},
        {'traveller_name': 'Maria', 'employee_id': 'Maria',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 1, 0), 'to_date': datetime(2017, 9, 13, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': 234}
    ]
    assert obtained == expected


def test_trip_that_does_not_cross_uk_does_not_extend_uk_period():
    employees = []
    trips = [
        create_trip('John', 'John', 'ITA', 'ITA', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(1, 0), pk=123),
        create_trip('John', 'John', 'ITA', 'GBR', 'ITA',
                    date(2017, 9, 13), time(0, 0),
                    date(2017, 9, 13), time(1, 0)),
        create_trip('John', 'John', 'ITA', 'BRA', 'ITA',
                    date(2017, 9, 15), time(0, 0),
                    date(2017, 9, 15), time(1, 0)),
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'John', 'employee_id': 'John',
         'category': TRAVEL_HISTORY_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 1, 0), 'to_date': datetime(2017, 9, 13, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': False, 'outbound_trip_id': None,
         'inbound_trip_id': 123},
    ]
    assert obtained == expected


def test_outbound_assumption_confirmation():
    employees = []
    trips = [
        create_trip('Maria', 'Maria', 'ESP', 'ESP', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(1, 0), pk=123),
        create_trip('Maria', 'Maria', 'ESP', 'BRA', 'ESP',
                    date(2017, 9, 13), time(0, 0),
                    date(2017, 9, 13), time(1, 0)),
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    outbound_assumption_confirmations = [
        create_outbound_assumption_confirmation('Maria', 'Maria',
                                                datetime(2017, 9, 11, 1, 0),
                                                correct_date=datetime(2017, 9, 12))
    ]
    obtained = process(employees, trips, home_country_clarifications,
                       assumptions, treaties,
                       outbound_assumption_confirmations=outbound_assumption_confirmations)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': 'Maria',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 1, 0), 'to_date': datetime(2017, 9, 12, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': 123}
    ]
    assert obtained == expected


def test_outbound_assumption_confirmation_without_non_crossing_trip():
    employees = []
    trips = [
        create_trip('Maria', 'Maria', 'ESP', 'ESP', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(1, 0), pk=123)
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    outbound_assumption_confirmations = [
        create_outbound_assumption_confirmation('Maria', 'Maria',
                                                datetime(2017, 9, 11, 1, 0),
                                                correct_date=datetime(2017, 9, 12))
    ]
    obtained = process(employees, trips, home_country_clarifications,
                       assumptions, treaties,
                       outbound_assumption_confirmations=outbound_assumption_confirmations)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': 'Maria',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 1, 0), 'to_date': datetime(2017, 9, 12, 0, 0),
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': 123}
    ]
    assert obtained == expected


def test_dont_use_next_non_uk_crossing_outbound_if_disabled_in_assumptions():
    employees = []
    trips = [
        create_trip('Maria', 'Maria', 'ESP', 'ESP', 'GBR',
                    date(2017, 9, 11), time(0, 0),
                    date(2017, 9, 11), time(1, 0), pk=123),
        create_trip('Maria', 'Maria', 'ESP', 'BRA', 'ESP',
                    date(2017, 9, 13), time(0, 0),
                    date(2017, 9, 13), time(1, 0)),
    ]
    home_country_clarifications = []
    assumptions = create_assumption(ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR,
                                    ASSUMPTION_IN_WITHOUT_OUT_TAX_YEAR_END)
    treaties = [
        create_treaty('ITA', date(2017, 4, 6), None)
    ]
    obtained = process(employees, trips, home_country_clarifications, assumptions, treaties)
    expected = [
        {'traveller_name': 'Maria', 'employee_id': 'Maria',
         'category': TRAVEL_HISTORY_NON_TREATY_COUNTRY,
         'from_date': datetime(2017, 9, 11, 1, 0), 'to_date': None,
         'originally_unclear': False, 'originally_assumed_inbound': False,
         'originally_assumed_outbound': True, 'outbound_trip_id': None,
         'inbound_trip_id': 123}
    ]
    assert obtained == expected
