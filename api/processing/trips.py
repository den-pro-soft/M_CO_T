"""This module provides a service for processing
raw travel data. See PROCESSING.md for details"""

from datetime import datetime


def process(raw_travel_data, border_cross_clarifications=None,
            ignored_employees=None, ignored_trips=None):
    """Process raw travel data"""

    border_cross_clarifs_by_key = {
        (clarif.employee_name, clarif.employee_id, clarif.border_cross,
         clarif.origin_country, clarif.destination_country): clarif
        for clarif in border_cross_clarifications
    } if border_cross_clarifications else {}

    ignored_employee_keys = {
        (emp.traveller_name, emp.employee_id)
        for emp in (
            ignored_employees
            if ignored_employees else []
        )
    }

    ignored_trip_keys = {
        (trip.traveller_name, trip.employee_id,
         trip.departure_date, trip.departure_time,
         trip.arrival_date, trip.arrival_time,
         trip.origin_country_name, trip.destination_country_name)
        for trip in (
            ignored_trips
            if ignored_trips else []
        )
    }

    for trip in raw_travel_data:

        employee_key = (trip.traveller_name, trip.employee_id)
        if employee_key in ignored_employee_keys:
            continue

        full_trip_key = (trip.traveller_name, trip.employee_id,
                         trip.departure_date, trip.departure_time,
                         trip.arrival_date, trip.arrival_time,
                         trip.origin_country_name, trip.destination_country_name)
        if full_trip_key in ignored_trip_keys:
            continue

        trip_key = (trip.traveller_name, trip.employee_id,
                    trip.border_cross,
                    trip.origin_country_name, trip.destination_country_name)

        if trip_key in border_cross_clarifs_by_key:
            correct_time = border_cross_clarifs_by_key[trip_key].correct_time
            border_cross_date_part = trip.border_cross.date()
            trip.border_cross = datetime.combine(border_cross_date_part, correct_time)
            trip_key = (trip.traveller_name, trip.employee_id,
                        trip.border_cross,
                        trip.origin_country_name, trip.destination_country_name)

        if not trip.domestic and not trip.invalid and not trip.ticket_type == 'Refund':
            yield trip
