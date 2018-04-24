# pylint: disable=C0111,W0611
"""Raw travel data processing test suite"""

from datetime import date, time, datetime
from models.travels import Travel, IgnoredEmployee, IgnoredTrip
from models.employees import BorderCrossTimeClarification
from .trips import process


# pylint: disable=C0103,R0914
def create_trip(traveller_name, employee_id, employee_country,
                origin, destination,
                departure_date, departure_time,
                arrival_date, arrival_time,
                ticket_type='Straight Ticket', invalid=False):
    pk = None
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
    border_cross = datetime.combine(departure_date, departure_time) if origin == 'GBR' else \
                   datetime.combine(arrival_date, arrival_time) if destination == 'GBR' else None
    return Travel(pk, traveller_data_id, traveller_name, employee_id,
                  employing_entity, employee_country, au, booking_date,
                  record_locator, ticket_no, ticket_type, segment_no,
                  calculated_seg_no, origin, origin_airport_code,
                  destination, destination_airport_code,
                  routing_airports, departure_date, departure_time,
                  arrival_date, arrival_time, invalid, row, border_cross)


# pylint: disable=C0103,R0914
def create_border_cross_clarification(traveller_name, employee_id, border_cross,
                                      origin_country, destination_country, correct_time):
    pk = None
    customer_id = None
    return BorderCrossTimeClarification(pk, customer_id, traveller_name, employee_id,
                                        border_cross, origin_country, destination_country,
                                        correct_time)


def create_ignored_employee(traveller_name, employee_id):
    pk = None
    customer_id = None
    return IgnoredEmployee(pk, customer_id, traveller_name, employee_id)


def create_ignored_trip(traveller_name, employee_id, origin, destination,
                        departure_date, departure_time,
                        arrival_date, arrival_time):
    pk = None
    customer_id = None
    return IgnoredTrip(pk, customer_id, traveller_name, employee_id,
                       origin, destination, departure_date, departure_time,
                       arrival_date, arrival_time)


def test_empty_list():
    raw_data = []
    obtained = list(process(raw_data))
    expected = []
    assert obtained == expected


def test_single_valid_trip():
    trip = create_trip('John', '123', 'GBR', origin='GBR', destination='ITA',
                       departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                       arrival_date=date(2017, 1, 1), arrival_time=time(11, 0))
    raw_data = [trip]
    obtained = list(process(raw_data))
    expected = [trip]
    assert obtained == expected


def test_non_uk_trip():
    trip = create_trip('John', '123', 'GBR', origin='BRA', destination='ITA',
                       departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                       arrival_date=date(2017, 1, 1), arrival_time=time(11, 0))
    raw_data = [trip]
    obtained = list(process(raw_data))
    expected = [trip]
    assert obtained == expected


def test_attached_errors():
    trip = create_trip('John', '123', 'GBR', origin='GBR', destination='ITA',
                       departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                       arrival_date=date(2017, 1, 1), arrival_time=time(11, 0),
                       invalid=True)
    raw_data = [trip]
    obtained = list(process(raw_data))
    expected = []
    assert obtained == expected


def test_duplicated_trip():
    trip = create_trip('John', '123', 'GBR', origin='GBR', destination='ITA',
                       departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                       arrival_date=date(2017, 1, 1), arrival_time=time(11, 0),
                       invalid=False)
    raw_data = [trip, trip]
    obtained = list(process(raw_data))
    expected = [trip, trip]
    assert obtained == expected


def test_refund_ticket():
    trip = create_trip('John', '123', 'GBR', origin='GBR', destination='ITA',
                       departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                       arrival_date=date(2017, 1, 1), arrival_time=time(11, 0),
                       invalid=False, ticket_type='Refund')
    raw_data = [trip]
    obtained = list(process(raw_data))
    expected = []
    assert obtained == expected


def test_domestic_flight():
    trip = create_trip('John', '123', 'GBR', origin='GBR', destination='GBR',
                       departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                       arrival_date=date(2017, 1, 1), arrival_time=time(11, 0))
    raw_data = [trip]
    obtained = list(process(raw_data))
    expected = []
    assert obtained == expected


def test_border_cross_time_clarification():
    border_cross_clarifications = [
        create_border_cross_clarification('John', '123',
                                          datetime(2017, 1, 1, 10, 0),
                                          'GBR', 'ITA', time(23, 45))
    ]
    raw_data = [
        create_trip('John', '123', 'GBR', origin='GBR', destination='ITA',
                    departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                    arrival_date=date(2017, 1, 1), arrival_time=time(11, 0))
    ]
    obtained = list(process(raw_data, border_cross_clarifications))
    assert len(obtained) == 1
    assert obtained[0].border_cross == datetime(2017, 1, 1, 23, 45)


def test_border_cross_time_clarification_duplication():
    border_cross_clarifications = [
        create_border_cross_clarification('John', '123',
                                          datetime(2017, 1, 1, 10, 0),
                                          'GBR', 'ITA', time(23, 45)),
    ]
    raw_data = [
        create_trip('John', '123', 'GBR', origin='GBR', destination='ITA',
                    departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                    arrival_date=date(2017, 1, 1), arrival_time=time(11, 0)),
        create_trip('John', '123', 'GBR', origin='GBR', destination='ITA',
                    departure_date=date(2017, 1, 1), departure_time=time(23, 45),
                    arrival_date=date(2017, 1, 1), arrival_time=time(23, 50)),
    ]
    obtained = list(process(raw_data, border_cross_clarifications))
    assert len(obtained) == 2
    assert obtained[0].border_cross == datetime(2017, 1, 1, 23, 45)
    assert obtained[1].border_cross == datetime(2017, 1, 1, 23, 45)


def test_without_employee_country():
    trip = create_trip('John', '123', None, origin='GBR', destination='ITA',
                       departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                       arrival_date=date(2017, 1, 1), arrival_time=time(11, 0))
    raw_data = [trip]
    obtained = list(process(raw_data))
    expected = [trip]
    assert obtained == expected


def test_ignored_employee():
    raw_data = [
        create_trip('John', '1', 'GBR', origin='GBR', destination='ITA',
                    departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                    arrival_date=date(2017, 1, 1), arrival_time=time(11, 0)),
        create_trip('Maria', '2', 'GBR', origin='GBR', destination='ITA',
                    departure_date=date(2017, 1, 1), departure_time=time(23, 45),
                    arrival_date=date(2017, 1, 1), arrival_time=time(23, 50)),
    ]
    ignored_employees = [
        create_ignored_employee('John', '1')
    ]
    obtained = list(process(raw_data, ignored_employees=ignored_employees))
    assert obtained == [raw_data[1]]


def test_ignored_trip():
    raw_data = [
        create_trip('John', '1', 'GBR', origin='GBR', destination='ITA',
                    departure_date=date(2017, 1, 1), departure_time=time(10, 0),
                    arrival_date=date(2017, 1, 1), arrival_time=time(11, 0)),
        create_trip('Maria', '2', 'GBR', origin='GBR', destination='ITA',
                    departure_date=date(2017, 1, 1), departure_time=time(23, 45),
                    arrival_date=date(2017, 1, 1), arrival_time=time(23, 50)),
    ]
    ignored_trips = [
        create_ignored_trip('John', '1', 'GBR', 'ITA',
                            date(2017, 1, 1), time(10, 0),
                            date(2017, 1, 1), time(11, 0))
    ]
    obtained = list(process(raw_data, ignored_trips=ignored_trips))
    assert obtained == [raw_data[1]]
