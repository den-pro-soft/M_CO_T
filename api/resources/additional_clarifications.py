"""Additional Clarifications REST resource"""

from uuid import uuid4
from datetime import datetime
from itertools import groupby
from flask import Blueprint, request, jsonify
from sqlalchemy import func, and_, case
from error_handling import InvalidUsage
import security
import validation as val
from models.storage import db, joinedload
from models.employees import HomeCountryClarification, InboundAssumptionConfirmation, \
                             BorderCrossTimeClarification, SamePersonConfirmation, \
                             OutboundAssumptionConfirmation
from models.employee_travel_history import EmployeeTravelHistory
from models.traveller_data_periods import TravellerDataPeriod
from models.traveller_data import TravellerData
from models.travels import Travel, IgnoredEmployee, IgnoredTrip
import tasks.refresh_employee_travel_history
from sqlalchemy import ARRAY
from sqlalchemy import String

# pylint: disable=C0103
bp = Blueprint('additional-clarifications', __name__)


TRAVEL_HISTORY_UK_EMPLOYEE = 1
TRAVEL_HISTORY_UK_EXPATRIATE = 6


@bp.route('', methods=['GET'])
def fetch():
    """Fetches additional clarifications"""
    user = security.authorize(request)

    customer = user.customer
    travel_history_ts = customer.last_available_travel_history

    ignored_employees = IgnoredEmployee.query \
                                       .filter_by(customer_id=customer.id) \
                                       .all()
    ignored_employees_keys = {
        (emp.traveller_name, emp.employee_id)
        for emp in ignored_employees
    }

    ignored_trips = IgnoredTrip.query \
                               .filter_by(customer_id=customer.id) \
                               .all()
    ignored_trips_keys = {
        (trip.traveller_name, trip.employee_id,
         trip.departure_date, trip.departure_time, trip.arrival_date, trip.arrival_time,
         trip.origin_country_name, trip.destination_country_name)
        for trip in ignored_trips
    }

    home_country_clarifications = HomeCountryClarification.query \
                                                          .filter_by(customer_id=customer.id) \
                                                          .all()

    home_country_clars_by_employee_key = {
        employee_key: sorted(clars, key=lambda clar: clar.to_date \
                                                    if clar.to_date else datetime(9999, 12, 31))
        for employee_key, clars in groupby(home_country_clarifications,
                                           lambda x: x.effective_employee_id)
    }

    def employee_home_country_clarifications(employee):
        """Returns a list with all home country clarifications given an employee key"""
        employee_key = employee[1] if employee[1] else employee[0]
        return home_country_clars_by_employee_key[employee_key] \
               if employee_key in home_country_clars_by_employee_key else []

    inb_assump_confirmations = InboundAssumptionConfirmation.query \
                                                            .filter_by(customer_id=customer.id) \
                                                            .all()

    inb_assump_by_trip_key = {
        (inb_assump.effective_employee_id, inb_assump.to_date): inb_assump
        for inb_assump in inb_assump_confirmations
    }

    def inbound_assumption_answer(history_entry):
        """Returns any existing answer for an inbound assumption confirmation, or None"""
        effective_employee_id = history_entry.employee_id if history_entry.employee_id \
                                else history_entry.traveller_name
        trip_key = (effective_employee_id, history_entry.to_date)
        if trip_key in inb_assump_by_trip_key:
            return 'Y' if inb_assump_by_trip_key[trip_key].confirmed else 'N'
        else:
            return None

    def inbound_assumption_correct_date(history_entry):
        """Returns any existing correct date for an inbound assumption confirmation, or None"""
        effective_employee_id = history_entry.employee_id if history_entry.employee_id \
                                else history_entry.traveller_name
        trip_key = (effective_employee_id, history_entry.to_date)
        correct_date = inb_assump_by_trip_key[trip_key].correct_date \
                       if trip_key in inb_assump_by_trip_key else None
        return correct_date.isoformat() if correct_date else None

    out_assump_confirmations = OutboundAssumptionConfirmation.query \
                                                             .filter_by(customer_id=customer.id) \
                                                             .all()

    out_assump_by_trip_key = {
        (out_assump.effective_employee_id, out_assump.from_date): out_assump
        for out_assump in out_assump_confirmations
    }

    def outbound_assumption_answer(history_entry):
        """Returns any existing answer for an outbound assumption confirmation, or None"""
        effective_employee_id = history_entry.employee_id if history_entry.employee_id \
                                else history_entry.traveller_name
        trip_key = (effective_employee_id, history_entry.from_date)
        if trip_key in out_assump_by_trip_key:
            return 'Y' if out_assump_by_trip_key[trip_key].confirmed else 'N'
        else:
            return None

    def outbound_assumption_correct_date(history_entry):
        """Returns any existing correct date for an outbound assumption confirmation, or None"""
        effective_employee_id = history_entry.employee_id if history_entry.employee_id \
                                else history_entry.traveller_name
        trip_key = (effective_employee_id, history_entry.from_date)
        correct_date = out_assump_by_trip_key[trip_key].correct_date \
                       if trip_key in out_assump_by_trip_key else None
        return correct_date.isoformat() if correct_date else None

    originally_unclear = EmployeeTravelHistory.query \
                                              .filter_by(customer_id=customer.id,
                                                         version_ts=travel_history_ts,
                                                         originally_unclear=True) \
                                              .order_by(EmployeeTravelHistory.traveller_name,
                                                        EmployeeTravelHistory.employee_id) \
                                              .all()

    originally_unclear_employees = {
        (history.traveller_name, history.employee_id)
        for history in originally_unclear
    }

    incomplete_trips = Travel.query \
                             .join(Travel.traveller_data) \
                             .join(TravellerData.traveller_data_periods) \
                             .filter(TravellerDataPeriod.customer_id == customer.id) \
                             .filter(Travel.invalid) \
                             .filter(Travel.ticket_type != 'Refund') \
                             .order_by(TravellerData.filename, Travel.row) \
                             .all()

    inbound_assumptions_filter = and_(EmployeeTravelHistory.customer_id == customer.id,
                                      EmployeeTravelHistory.version_ts == travel_history_ts,
                                      EmployeeTravelHistory.originally_assumed_inbound,
                                      ~EmployeeTravelHistory.category.in_([
                                          TRAVEL_HISTORY_UK_EMPLOYEE,
                                          TRAVEL_HISTORY_UK_EXPATRIATE,
                                      ]))
    outbound_trip_joined_load = joinedload('outbound_trip')
    traveller_data_joined_load = joinedload('outbound_trip.traveller_data')
    inbound_assumptions = EmployeeTravelHistory.query \
                                               .options(outbound_trip_joined_load) \
                                               .options(traveller_data_joined_load) \
                                               .filter(inbound_assumptions_filter) \
                                               .order_by(EmployeeTravelHistory.traveller_name,
                                                         EmployeeTravelHistory.employee_id) \
                                               .all()

    outbound_assumptions_filter = and_(EmployeeTravelHistory.customer_id == customer.id,
                                       EmployeeTravelHistory.version_ts == travel_history_ts,
                                       EmployeeTravelHistory.originally_assumed_outbound,
                                       ~EmployeeTravelHistory.category.in_([
                                           TRAVEL_HISTORY_UK_EMPLOYEE,
                                           TRAVEL_HISTORY_UK_EXPATRIATE,
                                       ]))
    inbound_trip_joined_load = joinedload('inbound_trip')
    inb_trav_data_joined_load = joinedload('inbound_trip.traveller_data')
    outbound_assumptions = EmployeeTravelHistory.query \
                                                .options(inbound_trip_joined_load) \
                                                .options(inb_trav_data_joined_load) \
                                                .filter(outbound_assumptions_filter) \
                                                .order_by(EmployeeTravelHistory.traveller_name,
                                                          EmployeeTravelHistory.employee_id) \
                                                .all()

    distinct_travels_ignored_trips = (
        and_(IgnoredTrip.customer_id == customer.id,
             IgnoredTrip.traveller_name == Travel.traveller_name,
             IgnoredTrip.employee_id == Travel.employee_id,
             IgnoredTrip.origin_country_name == Travel.origin_country_name,
             IgnoredTrip.destination_country_name == Travel.destination_country_name,
             IgnoredTrip.departure_date == Travel.departure_date,
             IgnoredTrip.departure_time == Travel.departure_time,
             IgnoredTrip.arrival_date == Travel.arrival_date,
             IgnoredTrip.arrival_time == Travel.arrival_time)
    )
    # pylint: disable=C0121
    distinct_travels = db.session.query(Travel.traveller_name,
                                        Travel.employee_id,
                                        Travel.border_cross,
                                        Travel.departure_date,
                                        Travel.arrival_date,
                                        Travel.origin_country_name,
                                        Travel.destination_country_name) \
                                 .join(Travel.traveller_data) \
                                 .join(TravellerData.traveller_data_periods) \
                                 .outerjoin(IgnoredTrip, distinct_travels_ignored_trips) \
                                 .filter(IgnoredTrip.id == None) \
                                 .filter(TravellerDataPeriod.customer_id == \
                                         customer.id) \
                                 .filter(Travel.invalid.is_(False)) \
                                 .filter(Travel.ticket_type != 'Refund') \
                                 .distinct() \
                                 .subquery()

    unclear_border = db.session.query(distinct_travels.c.traveller_name,
                                      distinct_travels.c.employee_id,
                                      distinct_travels.c.departure_date,
                                      distinct_travels.c.arrival_date,
                                      distinct_travels.c.border_cross) \
                                .group_by(distinct_travels.c.traveller_name,
                                          distinct_travels.c.employee_id,
                                          distinct_travels.c.departure_date,
                                          distinct_travels.c.arrival_date,
                                          distinct_travels.c.border_cross) \
                                .having(func.count(1) > 1) \
                                .subquery()

    unclear_border_join_conditions = and_(unclear_border.c.traveller_name == Travel.traveller_name,
                                          unclear_border.c.employee_id == Travel.employee_id,
                                          unclear_border.c.border_cross == Travel.border_cross,
                                          unclear_border.c.departure_date == Travel.departure_date,
                                          unclear_border.c.arrival_date == Travel.arrival_date)
    query = db.session.query(Travel.traveller_name,
                             Travel.employee_id,
                             Travel.border_cross,
                             Travel.origin_country_name,
                             Travel.destination_country_name,
                             Travel.departure_date,
                             Travel.departure_time,
                             Travel.arrival_date,
                             Travel.arrival_time,
                             Travel.row,
                             TravellerData.filename)
    unclear_border_cross_time = query.distinct() \
                                     .join(unclear_border, unclear_border_join_conditions) \
                                     .join(Travel.traveller_data) \
                                     .join(TravellerData.traveller_data_periods) \
                                     .filter(TravellerDataPeriod.customer_id == customer.id) \
                                     .filter(Travel.invalid.is_(False)) \
                                     .filter(Travel.ticket_type != 'Refund') \
                                     .order_by(Travel.traveller_name,
                                               Travel.employee_id,
                                               Travel.border_cross) \
                                     .all()

    border_cross_clarifs = BorderCrossTimeClarification.query \
                                                       .filter_by(customer_id=customer.id) \
                                                       .all()

    border_cross_clarifs_by_key = {
        (clarif.employee_name, clarif.employee_id, clarif.border_cross,
         clarif.origin_country, clarif.destination_country): clarif
        for clarif in border_cross_clarifs
    }

    def border_cross_time_correct_time(trip):
        """Returns any existing correct time for an unclear border cross time, or None"""
        trip_key = (trip.traveller_name, trip.employee_id, trip.border_cross,
                    trip.origin_country_name, trip.destination_country_name)
        correct_time = border_cross_clarifs_by_key[trip_key].correct_time \
                       if trip_key in border_cross_clarifs_by_key else None
        return correct_time.strftime("%H:%M") if correct_time else None

    # fetches every distinct combination of (effective_employee_id, traveller_name)
    # from the travels table that is not ignored

    effective_id_case_expression = case([(Travel.employee_id != '', Travel.employee_id)],
                                        else_=Travel.traveller_name)
    ignored_employee_join_expr = and_(IgnoredEmployee.customer_id == customer.id,
                                      IgnoredEmployee.traveller_name == Travel.traveller_name,
                                      IgnoredEmployee.employee_id == Travel.employee_id)
    # pylint: disable=C0121
    distinct_eff_ee_ids = db.session.query(effective_id_case_expression.label('eff_id'),
                                           Travel.traveller_name) \
                                    .join(Travel.traveller_data) \
                                    .join(TravellerData.traveller_data_periods) \
                                    .outerjoin(IgnoredEmployee, ignored_employee_join_expr) \
                                    .filter(TravellerDataPeriod.customer_id == customer.id) \
                                    .filter(IgnoredEmployee.id == None) \
                                    .distinct() \
                                    .subquery()

    # filters the query above keeping only the effective IDs
    # with at least two different traveller names

    duplicated_eff_ee_ids = db.session.query(distinct_eff_ee_ids.c.eff_id) \
                                      .group_by(distinct_eff_ee_ids.c.eff_id) \
                                      .having(func.count(1) > 1) \
                                      .subquery()

    # aggregates traveller names so we can present the user
    # which names are actually duplicated

    duplicated_ee_names = db.session.query(duplicated_eff_ee_ids.c.eff_id,Travel.traveller_name, func.array_agg(func.distinct(Travel.origin_country_name)) \
                            .label('origin_cnt'), func.array_agg(func.distinct(Travel.destination_country_name)).label('dest_cnt')) \
                            .group_by(Travel.traveller_name, duplicated_eff_ee_ids.c.eff_id) \
                            .filter(effective_id_case_expression ==duplicated_eff_ee_ids.c.eff_id) \
                            .join(Travel.traveller_data) \
                            .join(TravellerData.traveller_data_periods) \
                            .filter(TravellerDataPeriod.customer_id == customer.id) \
                            .filter(Travel.traveller_name != '') \
                            .order_by(duplicated_eff_ee_ids.c.eff_id) \
                            .distinct() \
                            .all()
    
    def get_base_name(name):
      if ' ' in name:
        name = name.replace(' ', '/')
      if name[:2].lower() == 'mr' or name[:2].lower() == 'ms' or name[:2].lower() == 'dr':
        return name[2:].split('/')
      if name[:4].lower() == 'miss':
        return name[4:].split('/')
      if name[-2:].lower() == 'mr' or name[-2:].lower() == 'ms' or name[-2:].lower() == 'dr':
        return name[:-2].split('/')
      if name[-4:].lower() == 'miss':
        return name[:-4].split('/')
      return name.split('/')

    tmp_duplicated_ee_names = duplicated_ee_names[:]

    for den in tmp_duplicated_ee_names:
      ds = [d for d in duplicated_ee_names if d.eff_id == den.eff_id]
      if len(ds) == 1:
        duplicated_ee_names.remove(ds[0])
        continue
      names = [d.traveller_name for d in ds]
      base_name = get_base_name(den.traveller_name)
      tmp = names[:]
      ds_len = len(ds)
      for idx, n in enumerate(tmp):
        t = n
        flg = 0
        t = t.replace(' ', '')
        for bn in base_name:
          if bn in t:
            if bn == 'R':
              if 'RMR' in t:
                t = t.replace('RMR', 'MR')
                continue
              elif 'RDR' in t:
                t = t.replace('RDR', 'DR')
                continue
            elif bn == 'S':
              if 'SMS' in t:
                t = t.replace('SMS', 'MS')
                continue
              elif 'SMISS' in t:
                t = t.replace('SMISS', 'MISS')
                continue
            elif bn == 'M':
              if 'MMS' in t:
                t = t.replace('MMS', 'MS')
                continue
              elif 'MMISS' in t:
                t = t.replace('MMISS', 'MISS')
                continue
            t = t.replace(bn, '')
          else:
            flg = 1
            break
        if flg == 1:
          continue
        t = t.replace('/', '').replace(' ', '').strip().lower()
        if t == 'mr' or t == 'ms' or t == 'miss' or t == 'dr' or t == '':
          if den.traveller_name != n:
              duplicated_ee_names.remove(ds[idx]);
              tmp_duplicated_ee_names.remove(ds[idx]);
              ds_len -= 1

      if ds_len == 1:
        if den in duplicated_ee_names:
          duplicated_ee_names.remove(den);

    #Loading ans save Orgin and Dest countries
    same_person_confirmations = SamePersonConfirmation.query \
                                                      .filter_by(customer_id=customer.id) \
                                                      .all()
    same_person_confirmations_ee_ids = [x.effective_employee_id for x in same_person_confirmations]
    #-----------------
    #-----------------

    return jsonify({
        "ignoredEmployees": list(map(lambda employee: {
            "id": employee.id,
            "travellerName": employee.traveller_name,
            "employeeId": employee.employee_id,
            "undoIgnore": False,
        }, ignored_employees)),
        "ignoredTrips": list(map(lambda trip: {
            "id": trip.id,
            "travellerName": trip.traveller_name,
            "employeeId": trip.employee_id,
            "origin": trip.origin_country_name,
            "destination": trip.destination_country_name,
            "departureDate": trip.departure_date.isoformat() if trip.departure_date else None,
            "departureTime": trip.departure_time.strftime('%H:%M') \
                             if trip.departure_time else None,
            "arrivalDate": trip.arrival_date.isoformat() if trip.arrival_date else None,
            "arrivalTime": trip.arrival_time.strftime('%H:%M') if trip.arrival_time else None,
            "undoIgnore": False,
        }, ignored_trips)),
        "unclearHomeCountry": list(map(lambda employee: {
            "travellerName": employee[0],
            "employeeId": employee[1],
            "ignore": False,
            "clarifications": list(map(lambda clarification: {
                "fromDate": clarification.from_date.isoformat() \
                            if clarification.from_date else None,
                "toDate": clarification.to_date.isoformat() \
                          if clarification.to_date else None,
                "homeCountry": clarification.home_country,
            }, employee_home_country_clarifications(employee))),
        }, filter(lambda employee: (employee[0], employee[1]) not in ignored_employees_keys,
                  originally_unclear_employees))),
        "incompleteTrips": list(map(lambda trip: {
            "id": trip.id,
            "travellerName": trip.traveller_name,
            "employeeId": trip.employee_id,
            "sourceSpreadsheet": trip.traveller_data.filename,
            "sourceRowNumber": trip.row,
            "departureDate": trip.departure_date.isoformat() if trip.departure_date else None,
            "departureTime": trip.departure_time.strftime('%H:%M') \
                             if trip.departure_time else None,
            "arrivalDate": trip.arrival_date.isoformat() if trip.arrival_date else None,
            "arrivalTime": trip.arrival_time.strftime('%H:%M') \
                           if trip.arrival_time else None,
            "originCountry": trip.origin_country_name,
            "destinationCountry": trip.destination_country_name,
        }, incomplete_trips)),
        "inboundAssumptions": list(map(lambda history_entry: {
            "travellerName": history_entry.traveller_name,
            "employeeId": history_entry.employee_id,
            "fromDate": history_entry.from_date.isoformat() if history_entry.from_date else None,
            "toDate": history_entry.to_date.isoformat() if history_entry.to_date else None,
            "inboundAssumptionConfirmed": inbound_assumption_answer(history_entry),
            "correctFromDate": inbound_assumption_correct_date(history_entry),
            "sourceSpreadsheet": history_entry.outbound_trip.traveller_data.filename \
                                 if history_entry.outbound_trip else None,
            "sourceRowNumber": history_entry.outbound_trip.row \
                               if history_entry.outbound_trip else None,
            "ignore": False,
            "outboundTrip": {
                "travellerName": history_entry.outbound_trip.traveller_name,
                "employeeId": history_entry.outbound_trip.employee_id,
                "originCountry": history_entry.outbound_trip.origin_country_name,
                "destinationCountry": history_entry.outbound_trip.destination_country_name,
                "departureDate": history_entry.outbound_trip.departure_date.isoformat() \
                                 if history_entry.outbound_trip.departure_date else None,
                "departureTime": history_entry.outbound_trip.departure_time.strftime('%H:%M') \
                                 if history_entry.outbound_trip.departure_time else None,
                "arrivalDate": history_entry.outbound_trip.arrival_date.isoformat() \
                                 if history_entry.outbound_trip.arrival_date else None,
                "arrivalTime": history_entry.outbound_trip.arrival_time.strftime('%H:%M') \
                                 if history_entry.outbound_trip.arrival_time else None,
            } if history_entry.outbound_trip else None,
        }, filter(lambda a: not a.outbound_trip or \
                            (a.outbound_trip.traveller_name, a.outbound_trip.employee_id,
                             a.outbound_trip.departure_date, a.outbound_trip.departure_time,
                             a.outbound_trip.arrival_date, a.outbound_trip.arrival_time,
                             a.outbound_trip.origin_country_name,
                             a.outbound_trip.destination_country_name) \
                            not in ignored_trips_keys,
                  inbound_assumptions))),
        "outboundAssumptions": list(map(lambda history_entry: {
            "travellerName": history_entry.traveller_name,
            "employeeId": history_entry.employee_id,
            "fromDate": history_entry.from_date.isoformat() if history_entry.from_date else None,
            "toDate": history_entry.to_date.isoformat() if history_entry.to_date else None,
            "outboundAssumptionConfirmed": outbound_assumption_answer(history_entry),
            "correctToDate": outbound_assumption_correct_date(history_entry),
            "sourceSpreadsheet": history_entry.inbound_trip.traveller_data.filename \
                                 if history_entry.inbound_trip else None,
            "sourceRowNumber": history_entry.inbound_trip.row \
                               if history_entry.inbound_trip else None,
            "ignore": False,
            "inboundTrip": {
                "travellerName": history_entry.inbound_trip.traveller_name,
                "employeeId": history_entry.inbound_trip.employee_id,
                "originCountry": history_entry.inbound_trip.origin_country_name,
                "destinationCountry": history_entry.inbound_trip.destination_country_name,
                "departureDate": history_entry.inbound_trip.departure_date.isoformat() \
                                 if history_entry.inbound_trip.departure_date else None,
                "departureTime": history_entry.inbound_trip.departure_time.strftime('%H:%M') \
                                 if history_entry.inbound_trip.departure_time else None,
                "arrivalDate": history_entry.inbound_trip.arrival_date.isoformat() \
                                 if history_entry.inbound_trip.arrival_date else None,
                "arrivalTime": history_entry.inbound_trip.arrival_time.strftime('%H:%M') \
                                 if history_entry.inbound_trip.arrival_time else None,
            } if history_entry.inbound_trip else None,
        }, filter(lambda a: not a.inbound_trip or \
                            (a.inbound_trip.traveller_name, a.inbound_trip.employee_id,
                             a.inbound_trip.departure_date, a.inbound_trip.departure_time,
                             a.inbound_trip.arrival_date, a.inbound_trip.arrival_time,
                             a.inbound_trip.origin_country_name,
                             a.inbound_trip.destination_country_name) \
                            not in ignored_trips_keys,
                  outbound_assumptions))),
        "unclearBorderCrossTime": list(map(lambda trip: {
            "travellerName": trip.traveller_name,
            "employeeId": trip.employee_id,
            "borderCross": trip.border_cross.isoformat(),
            "originCountry": trip.origin_country_name,
            "destinationCountry": trip.destination_country_name,
            "correctTime": border_cross_time_correct_time(trip),
            "departureDate": trip.departure_date.isoformat() \
                             if trip.departure_date else None,
            "departureTime": trip.departure_time.strftime('%H:%M') \
                             if trip.departure_time else None,
            "arrivalDate": trip.arrival_date.isoformat() \
                           if trip.arrival_date else None,
            "arrivalTime": trip.arrival_time.strftime('%H:%M') \
                           if trip.arrival_time else None,
            "sourceSpreadsheet": trip.filename,
            "sourceRowNumber": trip.row,
            "ignore": False,
        }, unclear_border_cross_time)),
        "duplicateIDs": list(map(lambda dup: {
            "effectiveEmployeeId": dup.eff_id,
            "travellerName": dup.traveller_name,
            "confirmed": dup.eff_id in same_person_confirmations_ee_ids,
            "originCountry": dup.origin_cnt,
            "destinationCountry": dup.dest_cnt,
            "ignore": False,
        }, duplicated_ee_names)),
    })


@bp.route('', methods=['PUT'])
def update():
    """Receives clarification answers and stores in the database"""
    user = security.authorize(request)
    customer = user.customer

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    check_input(data)

    home_country_clarifications = HomeCountryClarification.query \
                                                          .filter_by(customer_id=customer.id) \
                                                          .all()

    home_country_clars_by_employee_key = {
        employee_key: sorted(clars, key=lambda clar: clar.to_date \
                                                    if clar.to_date else datetime(9999, 12, 31))
        for employee_key, clars in groupby(home_country_clarifications,
                                           lambda x: x.effective_employee_id)
    }

    if 'ignoredEmployees' in data and isinstance(data['ignoredEmployees'], list):
        for ignored_employee in data['ignoredEmployees']:
            if 'undoIgnore' in ignored_employee and ignored_employee['undoIgnore']:
                ignored_employee_record = IgnoredEmployee.query.get(ignored_employee['id'])
                db.session.delete(ignored_employee_record)

    if 'ignoredTrips' in data and isinstance(data['ignoredTrips'], list):
        for ignored_trip in data['ignoredTrips']:
            if 'undoIgnore' in ignored_trip and ignored_trip['undoIgnore']:
                ignored_trip_record = IgnoredTrip.query.get(ignored_trip['id'])
                db.session.delete(ignored_trip_record)

    if 'unclearHomeCountry' in data and isinstance(data['unclearHomeCountry'], list):
        for employee in data['unclearHomeCountry']:
            employee_key = employee['employeeId'] if employee['employeeId'] \
                           else employee['travellerName']
            if employee_key in home_country_clars_by_employee_key:
                for existing_clarification in home_country_clars_by_employee_key[employee_key]:
                    db.session.delete(existing_clarification)
            for clar in employee['clarifications']:
                empty_clarification = not clar['homeCountry'] and \
                                      not clar['fromDate'] and \
                                      not clar['toDate']
                if not empty_clarification:
                    db.session.add(HomeCountryClarification(pk=uuid4(),
                                                            customer_id=customer.id,
                                                            effective_employee_id=employee_key,
                                                            home_country=clar['homeCountry'],
                                                            from_date=clar['fromDate'],
                                                            to_date=clar['toDate']))
            if 'ignore' in employee and employee['ignore']:
                db.session.add(IgnoredEmployee(pk=uuid4(),
                                               customer_id=customer.id,
                                               traveller_name=employee['travellerName'],
                                               employee_id=employee['employeeId']))

    traveller_data_periods = TravellerDataPeriod.query \
                                                .options(joinedload('traveller_data.travels')) \
                                                .filter_by(customer_id=customer.id) \
                                                .all()
    incomplete_trips = [trip \
                        for period in traveller_data_periods \
                        for trip in period.traveller_data.travels
                        if trip.invalid]
    incomplete_trips_by_id = {str(trip.id): trip for trip in incomplete_trips}

    if 'incompleteTrips' in data and isinstance(data['incompleteTrips'], list):
        for trip in data['incompleteTrips']:
            if trip['id'] in incomplete_trips_by_id:
                existing = incomplete_trips_by_id[trip['id']]
                existing.origin_country_name = trip['originCountry'] \
                                               if 'originCountry' in trip else None
                existing.destination_country_name = trip['destinationCountry'] \
                                                    if 'destinationCountry' in trip else None
                existing.departure_date = trip['departureDate']
                existing.departure_time = trip['departureTime']
                existing.arrival_date = trip['arrivalDate']
                existing.arrival_time = trip['arrivalTime']

                if trip['originCountry'] == 'GBR':
                    border_cross = (
                        datetime.combine(trip['departureDate'], trip['departureTime'])
                        if trip['departureDate'] and trip['departureTime']
                        else None
                    )
                else:
                    border_cross = (
                        datetime.combine(trip['arrivalDate'], trip['arrivalTime'])
                        if trip['arrivalDate'] and trip['arrivalTime']
                        else None
                    )

                existing.border_cross = border_cross
                existing.invalid = not existing.departure_date \
                                   or not existing.departure_time \
                                   or not existing.arrival_date \
                                   or not existing.arrival_time \
                                   or not existing.origin_country_name \
                                   or not existing.destination_country_name

    inb_assump_confirmations = InboundAssumptionConfirmation.query \
                                                            .filter_by(customer_id=customer.id) \
                                                            .all()

    inb_assump_by_trip_key = {
        (inb_assump.effective_employee_id, inb_assump.to_date): inb_assump
        for inb_assump in inb_assump_confirmations
    }

    if 'inboundAssumptions' in data and isinstance(data['inboundAssumptions'], list):
        for trip in data['inboundAssumptions']:
            if trip['inboundAssumptionConfirmed']:
                confirmed = trip['inboundAssumptionConfirmed']
                employee_key = trip['employeeId'] if trip['employeeId'] \
                               else trip['travellerName']
                trip_key = (employee_key, trip['toDate'])
                if trip_key in inb_assump_by_trip_key:
                    inb_assump = inb_assump_by_trip_key[trip_key]
                    inb_assump.confirmed = confirmed
                    inb_assump.correct_date = trip['correctFromDate'] if confirmed else None
                else:
                    inb_assump = InboundAssumptionConfirmation(uuid4(),
                                                               customer.id,
                                                               employee_key,
                                                               trip['toDate'],
                                                               confirmed,
                                                               trip['correctFromDate'])
                    db.session.add(inb_assump)
            if trip['ignore'] and trip['outboundTrip']:
                db.session.add(_create_ignored_trip(trip['outboundTrip'], customer.id))

    out_assump_confirmations = OutboundAssumptionConfirmation.query \
                                                             .filter_by(customer_id=customer.id) \
                                                             .all()

    out_assump_by_trip_key = {
        (out_assump.effective_employee_id, out_assump.from_date): out_assump
        for out_assump in out_assump_confirmations
    }

    if 'outboundAssumptions' in data and isinstance(data['outboundAssumptions'], list):
        for trip in data['outboundAssumptions']:
            if trip['outboundAssumptionConfirmed']:
                confirmed = trip['outboundAssumptionConfirmed']
                employee_key = trip['employeeId'] if trip['employeeId'] \
                               else trip['travellerName']
                trip_key = (employee_key, trip['fromDate'])
                if trip_key in out_assump_by_trip_key:
                    out_assump = out_assump_by_trip_key[trip_key]
                    out_assump.confirmed = confirmed
                    out_assump.correct_date = trip['correctToDate'] if confirmed else None
                else:
                    out_assump = OutboundAssumptionConfirmation(uuid4(),
                                                                customer.id,
                                                                employee_key,
                                                                trip['fromDate'],
                                                                confirmed,
                                                                trip['correctToDate'])
                    db.session.add(out_assump)
            if trip['ignore'] and trip['inboundTrip']:
                db.session.add(_create_ignored_trip(trip['inboundTrip'], customer.id))

    border_cross_clarifs = BorderCrossTimeClarification.query \
                                                       .filter_by(customer_id=customer.id) \
                                                       .all()

    border_cross_clarifs_by_key = {
        (clarif.employee_name, clarif.employee_id, clarif.border_cross,
         clarif.origin_country, clarif.destination_country): clarif
        for clarif in border_cross_clarifs
    }

    if 'unclearBorderCrossTime' in data and isinstance(data['unclearBorderCrossTime'], list):
        for trip in data['unclearBorderCrossTime']:
            if 'correctTime' not in trip or not trip['correctTime']:
                continue
            trip_key = (trip['travellerName'], trip['employeeId'], trip['borderCross'],
                        trip['originCountry'], trip['destinationCountry'])
            if trip_key in border_cross_clarifs_by_key:
                clarif = border_cross_clarifs_by_key[trip_key]
                clarif.correct_time = trip['correctTime']
            else:
                clarif = BorderCrossTimeClarification(uuid4(),
                                                      customer.id,
                                                      trip['travellerName'],
                                                      trip['employeeId'],
                                                      trip['borderCross'],
                                                      trip['originCountry'],
                                                      trip['destinationCountry'],
                                                      trip['correctTime'])
                db.session.add(clarif)
            if trip['ignore']:
                db.session.add(_create_ignored_trip(trip, customer.id))


    same_person_confirmations = SamePersonConfirmation.query \
                                                      .filter_by(customer_id=customer.id) \
                                                      .all()
    same_person_confirmations_by_id = {
        x.effective_employee_id: x \
        for x in same_person_confirmations
    }

    if 'duplicateIDs' in data and isinstance(data['duplicateIDs'], list):
        answers = {(x['effectiveEmployeeId'], x['confirmed']) for x in data['duplicateIDs']}
        for effective_id, confirmed in answers:
            record_exists = effective_id in same_person_confirmations_by_id
            if confirmed and not record_exists:

                same_person = SamePersonConfirmation(uuid4(),
                                                     customer.id,
                                                     effective_id)
                db.session.add(same_person)
            if not confirmed and record_exists:
                db.session.delete(same_person_confirmations_by_id[effective_id])

        for duplicate in data['duplicateIDs']:
            if 'ignore' in duplicate and duplicate['ignore']:
                db.session.add(IgnoredEmployee(pk=uuid4(),
                                               customer_id=customer.id,
                                               traveller_name=duplicate['travellerName'],
                                               employee_id=duplicate['effectiveEmployeeId']))

    db.session.commit()
    tasks.refresh_employee_travel_history.schedule(user.customer.id)

    return ('', 204)


def check_input(data):
    """Check the validity of input data"""
    errors = []

    if 'unclearHomeCountry' in data and isinstance(data['unclearHomeCountry'], list):
        for idx, employee in enumerate(data['unclearHomeCountry']):
            traveller_name = employee['travellerName'] if employee['travellerName'] else 'Unnamed'
            employee_id = employee['employeeId'] if employee['employeeId'] else 'No ID'
            error_prefix = '{0} ({1})'.format(traveller_name, employee_id)
            check_home_country_clarifications(errors, error_prefix, employee)

    if 'incompleteTrips' in data and isinstance(data['incompleteTrips'], list):
        for idx, trip in enumerate(data['incompleteTrips']):
            error_prefix = 'Line #{0}: '.format(idx + 1)
            if trip['departureDate']:
                trip['departureDate'] = val.check_date(errors, trip['departureDate'],
                                                       '{0}Departure date'.format(error_prefix))
            if trip['departureTime']:
                trip['departureTime'] = val.check_time(errors, trip['departureTime'],
                                                       '{0}Departure time'.format(error_prefix))
            if trip['arrivalDate']:
                trip['arrivalDate'] = val.check_date(errors, trip['arrivalDate'],
                                                     '{0}Arrival date'.format(error_prefix))
            if trip['arrivalTime']:
                trip['arrivalTime'] = val.check_time(errors, trip['arrivalTime'],
                                                     '{0}Arrival time'.format(error_prefix))

    if 'inboundAssumptions' in data and isinstance(data['inboundAssumptions'], list):
        for idx, trip in enumerate(data['inboundAssumptions']):
            error_prefix = 'Line #{0}: '.format(idx + 1)
            trip['toDate'] = val.check_date(errors, trip['toDate'],
                                            '{0}To date'.format(error_prefix))
            if trip['inboundAssumptionConfirmed'] and trip['inboundAssumptionConfirmed'] == 'N':
                if 'correctFromDate' not in trip or not trip['correctFromDate']:
                    errors.append('{0}Correct date is required for a "No" answer' \
                                  .format(error_prefix))
                else:
                    trip['correctFromDate'] = val.check_date(errors, trip['correctFromDate'],
                                                             '{0}Correct date' \
                                                             .format(error_prefix))
                    if trip['correctFromDate'] and trip['toDate'] \
                       and trip['correctFromDate'] > trip['toDate']:
                        errors.append('{0}Correct date must be equal or less than To date' \
                                      .format(error_prefix))

    if 'outboundAssumptions' in data and isinstance(data['outboundAssumptions'], list):
        for idx, trip in enumerate(data['outboundAssumptions']):
            error_prefix = 'Line #{0}: '.format(idx + 1)
            trip['fromDate'] = val.check_date(errors, trip['fromDate'],
                                              '{0}From date'.format(error_prefix))
            if trip['outboundAssumptionConfirmed'] and trip['outboundAssumptionConfirmed'] == 'N':
                if 'correctToDate' not in trip or not trip['correctToDate']:
                    errors.append('{0}Correct date is required for a "No" answer' \
                                  .format(error_prefix))
                else:
                    trip['correctToDate'] = val.check_date(errors, trip['correctToDate'],
                                                           '{0}Correct date' \
                                                           .format(error_prefix))
                    if trip['correctToDate'] and trip['fromDate'] \
                       and trip['correctToDate'] < trip['fromDate']:
                        errors.append('{0}Correct date must be equal or after From date' \
                                      .format(error_prefix))

    if 'unclearBorderCrossTime' in data and isinstance(data['unclearBorderCrossTime'], list):
        for trip in data['unclearBorderCrossTime']:
            employee_name = trip['travellerName'] if trip['travellerName'] else 'Unnamed'
            employee_id = trip['employeeId'] if trip['employeeId'] else 'N/A'
            border_cross = val.check_date(errors, trip['borderCross'], 'Border Cross Date')
            border_cross_fmtd = border_cross.strftime("%d/%m/%y %H:%M") if border_cross else '?'
            error_prefix = '{0} ({1}) - {2} - {3}/{4}: '.format(employee_name,
                                                                employee_id,
                                                                border_cross_fmtd,
                                                                trip['originCountry'],
                                                                trip['destinationCountry'])
            if 'correctTime' in trip:
                trip['correctTime'] = val.check_time(errors, trip['correctTime'],
                                                     '{0}Correct Time'.format(error_prefix))

    if errors:
        raise InvalidUsage(errors)


def check_home_country_clarifications(errors, employee_error_prefix, employee):
    """Checks all the employee home country clarifications"""
    if 'clarifications' in employee and isinstance(employee['clarifications'], list):
        last_eff_date = None
        for idx, clar in enumerate(employee['clarifications']):
            empty_clarification = not clar['homeCountry'] and \
                                  not clar['fromDate'] and not clar['toDate']
            if empty_clarification:
                continue
            error_prefix = "{0} - Clarification #{1}".format(employee_error_prefix, idx + 1)
            empty_country = 'homeCountry' not in clar or not clar['homeCountry']
            if empty_country:
                errors.append('{0}: Home country is required'.format(error_prefix))
            eff_from = None
            empty_eff_from = 'fromDate' not in clar or not clar['fromDate']
            if not empty_eff_from:
                eff_from = val.check_date(errors, clar['fromDate'],
                                          '{0}: From Date'.format(error_prefix))
            eff_to = None
            empty_eff_to = 'toDate' not in clar or not clar['toDate']
            if not empty_eff_to:
                eff_to = val.check_date(errors, clar['toDate'],
                                        '{0}: To Date'.format(error_prefix))
            if eff_from and eff_to and eff_to < eff_from:
                errors.append('{0}: To Date must be after From Date'
                              .format(error_prefix))
            if last_eff_date:
                if eff_from and last_eff_date >= eff_from:
                    errors.append('{0}: From Date must be after previous clarifications'
                                  .format(error_prefix))
                elif eff_to and last_eff_date >= eff_to:
                    errors.append('{0}: To Date must be after previous clarifications'
                                  .format(error_prefix))
            last_eff_date = eff_to if eff_to else eff_from if eff_from else last_eff_date


def _create_ignored_trip(trip, customer_id):
    return IgnoredTrip(pk=uuid4(),
                       customer_id=customer_id,
                       traveller_name=trip['travellerName'],
                       employee_id=trip['employeeId'],
                       origin_country_name=trip['originCountry'],
                       destination_country_name=trip['destinationCountry'],
                       departure_date=trip['departureDate'],
                       departure_time=trip['departureTime'],
                       arrival_date=trip['arrivalDate'],
                       arrival_time=trip['arrivalTime'])