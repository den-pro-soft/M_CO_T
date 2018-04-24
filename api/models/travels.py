"""Information about Travels"""

from sqlalchemy import Column, String, Integer, Date, Time, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from .storage import db
from .custom_types import GUID


class Travel(db.Model):
    """Travel model class"""
    __tablename__ = 'travels'

    # pylint: disable=C0103,R0914
    def __init__(self, pk, traveller_data_id, traveller_name, employee_id,
                 employing_entity, employee_country, au, booking_date,
                 record_locator, ticket_no, ticket_type, segment_no,
                 calculated_seg_no, origin_country_name, origin_airport_code,
                 destination_country_name, destination_airport_code,
                 routing_airports, departure_date, departure_time,
                 arrival_date, arrival_time, invalid, row, border_cross):
        self.id = pk
        self.traveller_data_id = traveller_data_id
        self.traveller_name = traveller_name
        self.employee_id = employee_id
        self.employing_entity = employing_entity
        self.employee_country = employee_country
        self.au = au
        self.booking_date = booking_date
        self.record_locator = record_locator
        self.ticket_no = ticket_no
        self.ticket_type = ticket_type
        self.segment_no = segment_no
        self.calculated_seg_no = calculated_seg_no
        self.origin_country_name = origin_country_name
        self.origin_airport_code = origin_airport_code
        self.destination_country_name = destination_country_name
        self.destination_airport_code = destination_airport_code
        self.routing_airports = routing_airports
        self.departure_date = departure_date
        self.departure_time = departure_time
        self.arrival_date = arrival_date
        self.arrival_time = arrival_time
        self.invalid = invalid
        self.row = row
        self.border_cross = border_cross

    # pylint: disable=C0103
    id = Column(GUID, primary_key=True)
    traveller_data_id = Column(GUID, ForeignKey('traveller_data.id'))
    traveller_data = relationship('TravellerData',
                                  backref=backref('travels',
                                                  lazy='raise',
                                                  cascade='all, delete-orphan'))
    traveller_name = Column(String)
    employee_id = Column(String)
    employing_entity = Column(String)
    employee_country = Column(String)
    au = Column(String)
    booking_date = Column(Date)
    record_locator = Column(String)
    ticket_no = Column(String)
    ticket_type = Column(String)
    segment_no = Column(String)
    calculated_seg_no = Column(String)
    origin_country_name = Column(String)
    origin_airport_code = Column(String)
    destination_country_name = Column(String)
    destination_airport_code = Column(String)
    routing_airports = Column(String)
    departure_date = Column(Date)
    departure_time = Column(Time)
    arrival_date = Column(Date)
    arrival_time = Column(Time)
    invalid = Column(Boolean)
    row = Column(Integer)
    border_cross = Column(DateTime)

    @property
    def effective_employee_id(self):
        """Returns the effective employee ID, i.e. their ID or their name if ID is blank"""
        return self.employee_id if self.employee_id else self.traveller_name

    @property
    def domestic(self):
        """Returns true if origin and destination is UK"""
        from_uk = self.origin_country_name == 'GBR'
        to_uk = self.destination_country_name == 'GBR'
        return from_uk and to_uk

    def cross_uk_borders(self):
        """Returns true if origin or destination is UK"""
        from_uk = self.origin_country_name == 'GBR'
        to_uk = self.destination_country_name == 'GBR'
        touch_uk = from_uk or to_uk
        domestic = from_uk and to_uk
        return touch_uk and not domestic


class TravellerDataError(db.Model):
    """Represents an error inside a traveller data spreadsheet"""
    __tablename__ = 'traveller_data_errors'

    # pylint: disable=C0103
    def __init__(self, pk, travel_id, error_code):
        self.id = pk
        self.travel_id = travel_id
        self.error_code = error_code

    # pylint: disable=C0103
    id = Column(Integer, primary_key=True)
    travel_id = Column(GUID)
    error_code = Column(Integer)


TRAVELLER_DATA_ERROR_CODES = {
    'INVALID_ORIGIN_COUNTRY': 2,
    'INVALID_DESTINATION_COUNTRY': 3,
    'INVALID_BOOKING_DATE': 4,
    'INVALID_DEPARTURE_DATE': 5,
    'INVALID_ARRIVAL_DATE': 7,
    'INCOMPLETE': 9,
}


class IgnoredEmployee(db.Model):
    """Represents an employee that should be ignored in trips processing"""
    __tablename__ = 'ignored_employees'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, traveller_name, employee_id):
        self.id = pk
        self.customer_id = customer_id
        self.traveller_name = traveller_name
        self.employee_id = employee_id

    # pylint: disable=C0103
    id = Column(Integer, primary_key=True)
    customer_id = Column(GUID)
    traveller_name = Column(String)
    employee_id = Column(String)


class IgnoredTrip(db.Model):
    """Represents a trip that should be ignored in trips processing"""
    __tablename__ = 'ignored_trips'

    # pylint: disable=C0103
    def __init__(self, pk, customer_id, traveller_name, employee_id,
                 origin_country_name, destination_country_name,
                 departure_date, departure_time, arrival_date, arrival_time):
        self.id = pk
        self.customer_id = customer_id
        self.traveller_name = traveller_name
        self.employee_id = employee_id
        self.origin_country_name = origin_country_name
        self.destination_country_name = destination_country_name
        self.departure_date = departure_date
        self.departure_time = departure_time
        self.arrival_date = arrival_date
        self.arrival_time = arrival_time

    # pylint: disable=C0103
    id = Column(Integer, primary_key=True)
    customer_id = Column(GUID)
    traveller_name = Column(String)
    employee_id = Column(String)
    origin_country_name = Column(String)
    destination_country_name = Column(String)
    departure_date = Column(Date)
    departure_time = Column(Time)
    arrival_date = Column(Date)
    arrival_time = Column(Time)
