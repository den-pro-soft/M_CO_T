"""This module provides a service for processing
employee travel history. See PROCESSING.md for details"""

from itertools import groupby
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import dates


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


def _group_employees_by_key(employees):
    """Group employees by effective ID"""
    return {
        emp.effective_id: emp
        for emp in employees
    }


def _group_clarifications_by_employee(clarifications):
    """Group home country clarifications by employee effective ID"""
    return {
        employee_key: sorted(clars, key=lambda clar: clar.to_date \
                                                    if clar.to_date else datetime(9999, 12, 31))
        for employee_key, clars in groupby(clarifications, lambda x: x.effective_employee_id)
    }


def _group_trips_by_employee(trips):
    """Group trips by employee effective ID"""
    previous_employee_key = None
    employee_trips = []
    for trip in trips:
        employee_key = trip.effective_employee_id
        if previous_employee_key is None:
            employee_trips.append(trip)
            previous_employee_key = employee_key
        elif previous_employee_key == employee_key:
            employee_trips.append(trip)
        else:
            yield (previous_employee_key, employee_trips)
            previous_employee_key = employee_key
            employee_trips = [trip]
    if employee_trips:
        yield previous_employee_key, employee_trips


def _identify_employee_category(work_arrangement_category, employee_country, from_date, treaties):
    """"Try to identify travel category based on employee data"""
    if work_arrangement_category:
        if work_arrangement_category == WORK_ARRANGEMENT_UK_EMPLOYEE:
            if not employee_country or employee_country == 'GBR':
                return TRAVEL_HISTORY_UK_EMPLOYEE
            else:
                return TRAVEL_HISTORY_UNKNOWN
        elif work_arrangement_category == WORK_ARRANGEMENT_UK_EXPATRIATE:
            return TRAVEL_HISTORY_UK_EXPATRIATE
        elif work_arrangement_category == WORK_ARRANGEMENT_OVERSEAS_BRANCH:
            return TRAVEL_HISTORY_OVERSEAS_BRANCH_VISITOR
        elif work_arrangement_category == WORK_ARRANGEMENT_NT_STA:
            if not employee_country or employee_country == 'GBR':
                return TRAVEL_HISTORY_UNKNOWN
            else:
                return _country_to_travel_category(employee_country, from_date, treaties)
        else:
            raise Exception('Unknown work arrangement category: {0}' \
                            .format(work_arrangement_category))
    elif employee_country:
        return _country_to_travel_category(employee_country, from_date, treaties)
    return TRAVEL_HISTORY_UNKNOWN


def _has_treaty(country, when, treaties):
    """Tries to find a treaty for the given country"""
    return [treaty for treaty in treaties \
            if treaty.country_code == country \
            and treaty.from_date <= when \
            and (not treaty.to_date or treaty.to_date >= when)]


def _country_to_travel_category(country_code, when, treaties):
    """Translates a country code + date to a travel history category"""
    if country_code == 'GBR':
        return TRAVEL_HISTORY_UK_EMPLOYEE
    elif _has_treaty(country_code, when.date(), treaties):
        return TRAVEL_HISTORY_TREATY_COUNTRY
    else:
        return TRAVEL_HISTORY_NON_TREATY_COUNTRY


def _assume_from_date(assumptions, to_date):
    """Assumes the start of period based on the end of it
    and client assumptions"""
    if not assumptions or not assumptions.outbound_uk_without_inbound:
        return dates.start_of_tax_year(to_date)
    else:
        assumption = assumptions.outbound_uk_without_inbound
        if assumption == ASSUMPTION_OUT_WITHOUT_IN_TAX_YEAR:
            return dates.start_of_tax_year(to_date)
        elif assumption == ASSUMPTION_OUT_WITHOUT_IN_TAX_MONTH:
            return dates.start_of_tax_month(to_date)
        elif assumption == ASSUMPTION_OUT_WITHOUT_IN_SAME_DAY:
            return to_date
        else:
            raise Exception('Unknown outbound without inbound assumption: {0}'.format(assumption))


# pylint: disable=C0103
def _identify_periods(trips, assumptions, employee, employee_key,
                      inbound_assumption_confirmations, outbound_assumption_confirmations):
    """Identify all periods in UK based on a
    collection of trips and work arrangements"""

    # first we need to aggregate events
    # outbound trips: ('OF', border cross date/time, employee country,
    #                  None, trip id, arrival date, cross_uk)
    # inbound trips: ('IF', border cross date/time, employee country,
    #                 None, trip id, departure date, cross_uk)
    # new work arrangement ('AS', when, None, work_arrangement_category, None, when, None)
    # end of work arrangement ('AE', when, None, work_arrangement_category, None, when, None)
    outbound_trips = [('OF', trip.border_cross, trip.employee_country,
                       None, trip.id, trip.arrival_date, trip.cross_uk_borders()) \
                      for trip in trips if trip.destination_country_name != 'GBR']
    inbound_trips = [('IF', trip.border_cross, trip.employee_country,
                      None, trip.id, trip.departure_date, trip.cross_uk_borders()) \
                     for trip in trips if trip.destination_country_name == 'GBR']
    arrangements = []
    for arr in employee.arrangements if employee and employee.arrangements else []:
        from_event_date = datetime.combine(arr.effective_from, time(0, 0)) \
                          if arr.effective_from else datetime(1, 1, 1, 0, 0, 0)
        arrangements.append(('AS', from_event_date, None, arr.category,
                             None, from_event_date, None))
        if arr.effective_to:
            to_event_date = datetime.combine(arr.effective_to, time(23, 59, 59))
            arrangements.append(('AE', to_event_date, None, arr.category,
                                 None, to_event_date, None))
    events = outbound_trips + inbound_trips + arrangements
    sorted_events = sorted(events, key=lambda e: (e[1], e[5]))

    inb_assu_by_key = {
        (inb_assump.effective_employee_id, inb_assump.to_date): inb_assump
        for inb_assump in inbound_assumption_confirmations
    } if inbound_assumption_confirmations else {}

    out_assu_by_key = {
        (out_assump.effective_employee_id, out_assump.from_date): out_assump
        for out_assump in outbound_assumption_confirmations
    } if outbound_assumption_confirmations else {}

    periods = []

    from_date = None
    from_country = None
    work_arrangement = None
    outbound_trip_id = None
    inbound_trip_id = None

    can_use_non_crossing_outbounds = (
        not assumptions or
        assumptions.inbound_uk_without_outbound == ASSUMPTION_IN_WITHOUT_OUT_TRY_NON_CROSSING
    )

    for event_type, event_date, event_employee_country, \
        event_work_arrangement, trip_id, _, cross_uk_borders in sorted_events:

        if event_type == 'OF':
            if not can_use_non_crossing_outbounds and not cross_uk_borders:
                continue
            outbound_trip_id = trip_id
            to_date = event_date
            if from_date or (cross_uk_borders and not periods):
                assumed_inbound = False
                if not from_date:
                    inbound_assumption_key = (employee_key, to_date)
                    if inbound_assumption_key in inb_assu_by_key:
                        from_date = inb_assu_by_key[inbound_assumption_key].correct_date
                    else:
                        from_date = _assume_from_date(assumptions, to_date)
                    assumed_inbound = True
                assumed_outbound = not cross_uk_borders
                if assumed_outbound:
                    outbound_assumption_key = (employee_key, from_date)
                    if outbound_assumption_key in out_assu_by_key:
                        to_date = out_assu_by_key[outbound_assumption_key].correct_date
                periods.append((from_date, to_date, event_employee_country,
                                work_arrangement, assumed_inbound, outbound_trip_id,
                                assumed_outbound, inbound_trip_id))
                from_date = None
            elif cross_uk_borders:
                # increment last period
                last_period = periods[-1]
                last_home_country = last_period[2]
                # if there is a mismatch we need to
                # consider unclear home country
                new_employee_country = last_home_country \
                                       if last_home_country == event_employee_country \
                                       else None
                periods[-1] = (last_period[0], to_date, new_employee_country,
                               last_period[3], last_period[4], outbound_trip_id,
                               False, last_period[7])
        elif event_type == 'IF':
            if not from_date:
                from_date = event_date
                inbound_trip_id = trip_id
            from_country = event_employee_country
        elif event_type == 'AS':
            if from_date and work_arrangement != event_work_arrangement:
                to_date = event_date - relativedelta(seconds=1)
                periods.append((from_date, to_date, from_country,
                                work_arrangement, False, outbound_trip_id,
                                False, inbound_trip_id))
                from_date = event_date
            work_arrangement = event_work_arrangement
        elif event_type == 'AE':
            pass
        else:
            raise Exception('Unknown event type: {0}'.format(event_type))

    if from_date:
        outbound_assumption_key = (employee_key, from_date)
        to_date = (
            out_assu_by_key[outbound_assumption_key].correct_date
            if outbound_assumption_key in out_assu_by_key
            else None
        )
        periods.append((from_date, to_date, from_country, work_arrangement,
                        False, outbound_trip_id, True, inbound_trip_id))

    return periods


# pylint: disable=C0103
def process(employees, trips, home_country_clarifications, \
            assumptions, treaties, inbound_assumption_confirmations=None,
            outbound_assumption_confirmations=None):
    """Calculates employee travel history"""

    result = []

    employees_by_key = _group_employees_by_key(employees)
    clarifications_by_employee_key = _group_clarifications_by_employee(home_country_clarifications)
    trips_by_employee = _group_trips_by_employee(trips)

    for employee_key, employee_trips in trips_by_employee:
        employee = employees_by_key[employee_key] if employee_key in employees_by_key else None
        clarifications = clarifications_by_employee_key[employee_key] \
                         if employee_key in clarifications_by_employee_key else {}
        periods = _identify_periods(employee_trips, assumptions, employee,
                                    employee_key, inbound_assumption_confirmations,
                                    outbound_assumption_confirmations)
        employee_id = next((x.employee_id for x in employee_trips if x.employee_id), '')
        employee_name = next((x.traveller_name for x in employee_trips if x.traveller_name), '')
        for from_date, to_date, employee_country, \
            work_arrangement_category, originally_assumed_inbound, \
            outbound_trip_id, originally_assumed_outbound, inbound_trip_id \
            in periods:

            category = _identify_employee_category(work_arrangement_category, employee_country,
                                                   from_date, treaties)

            originally_unclear = category == TRAVEL_HISTORY_UNKNOWN
            if originally_unclear:
                intervals = []
                next_interval_start = from_date
                for clar in clarifications:
                    intersection_at_to_date = not clar.from_date \
                                              or not to_date or clar.from_date <= to_date
                    intersection_at_from_date = not clar.to_date or not next_interval_start \
                                                or clar.to_date >= next_interval_start
                    if intersection_at_to_date and intersection_at_from_date:
                        if not next_interval_start or \
                           (clar.from_date and next_interval_start < clar.from_date):
                            prefix_interval_end = clar.from_date - relativedelta(days=1)
                            intervals.append({
                                'from_date': next_interval_start,
                                'to_date': datetime(
                                    prefix_interval_end.year,
                                    prefix_interval_end.month,
                                    prefix_interval_end.day,
                                    23, 59
                                ),
                                'category': TRAVEL_HISTORY_UNKNOWN,
                            })
                            next_interval_start = clar.from_date
                        if to_date and clar.to_date:
                            interval_end = min(to_date, clar.to_date)
                        elif clar.to_date:
                            interval_end = clar.to_date
                        else:
                            interval_end = to_date
                        intervals.append({
                            'from_date': next_interval_start,
                            'to_date': interval_end,
                            'category': _country_to_travel_category(clar.home_country,
                                                                    next_interval_start,
                                                                    treaties),
                        })
                        if interval_end:
                            interval_end_plus_one = interval_end + relativedelta(days=1)
                            next_interval_start = datetime(
                                interval_end_plus_one.year,
                                interval_end_plus_one.month,
                                interval_end_plus_one.day
                            )
                        else:
                            next_interval_start = None
                            break
                if next_interval_start and (not to_date or next_interval_start <= to_date):
                    intervals.append({
                        'from_date': next_interval_start,
                        'to_date': to_date,
                        'category': TRAVEL_HISTORY_UNKNOWN,
                    })
            else:
                intervals = [{'from_date': from_date, 'to_date': to_date, 'category': category}]

            for interval in intervals:
                result.append({
                    'traveller_name': employee_name,
                    'employee_id': employee_id,
                    'category': interval['category'],
                    'from_date': interval['from_date'],
                    'to_date': interval['to_date'],
                    'originally_unclear': originally_unclear,
                    'originally_assumed_inbound': originally_assumed_inbound,
                    'originally_assumed_outbound': originally_assumed_outbound,
                    'outbound_trip_id': outbound_trip_id,
                    'inbound_trip_id': inbound_trip_id,
                })

    return result
