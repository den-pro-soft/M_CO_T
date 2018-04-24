"""REST resource responsible for report results"""


from uuid import uuid4
from flask import Blueprint, request, jsonify
import security
import validation as val
from error_handling import InvalidUsage
from models.storage import db
from models.traveller_data_periods import TravellerDataPeriod
from models.employee_travel_history import EmployeeTravelHistory
from models.companies_infos import CompaniesInfo
from models.report_periods import ReportPeriod
import processing.report_results
# pylint: disable=C0103
bp = Blueprint('report-results', __name__)


@bp.route('', methods=['POST'])
def fetch():
    """Fetches most recent report results"""
    user = security.authorize(request)
    customer = user.customer
    last_request = customer.last_travel_history_request
    last_error = customer.last_travel_history_error
    available_data = customer.last_available_travel_history

    companies_info = CompaniesInfo.query.filter_by(customer_id=user.customer.id).first()
    progress_event_channel = 'travel-history-processing-progress-{0}-{1}' \
                                .format(customer.id, last_request.isoformat()) \
                             if last_request and (not available_data \
                                                  or last_request > available_data) \
                             else None

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    check_input(data)

    emp_travel_history_entities = EmployeeTravelHistory.query \
                                                       .filter_by(customer_id=customer.id,
                                                                  version_ts=available_data) \
                                                       .all()
    emp_travel_history = [
        {'traveller_name': entry.traveller_name, 'employee_id': entry.employee_id,
         'category': entry.category,
         'from_date': entry.from_date, 'to_date': entry.to_date,
         'originally_unclear': entry.originally_unclear,
         'originally_assumed_inbound': entry.originally_assumed_inbound,
         'outbound_trip_id': entry.outbound_trip_id}
        for entry in emp_travel_history_entities
    ]

    report_periods = ReportPeriod.query \
                                 .filter_by(user_id=user.id) \
                                 .all()

    results_per_category = {}
    categories = data['categories']
    for category in categories:

        report_period = next((x for x in report_periods \
                              if x.treaty_position == int(category)), None)

        if 'fromDate' in data and data['fromDate'] and \
           'toDate' in data and data['toDate']:
            from_date = data['fromDate'].date()
            to_date = data['toDate'].date()
            if report_period:
                report_period.from_date = from_date
                report_period.to_date = to_date
            else:
                db.session.add(ReportPeriod(uuid4(), user.id, category,
                                            from_date, to_date))
        elif report_period:
            from_date = report_period.from_date
            to_date = report_period.to_date
        else:
            latest_period = TravellerDataPeriod.query \
                                               .filter_by(customer_id=customer.id) \
                                               .order_by(TravellerDataPeriod.from_date.desc()) \
                                               .first()
            if latest_period:
                from_date = latest_period.from_date
                to_date = latest_period.to_date
            else:
                from_date = None
                to_date = None

        employees = processing.report_results.process(emp_travel_history,
                                                      from_date, to_date,
                                                      [category]) \
                    if from_date and to_date else []

        results_per_category[category] = {
            "stays": [{
                "travellerName": employee['traveller_name'],
                "employeeId": employee['employee_id'],
                "days": stay['days'],
            } for employee in employees for stay in employee['stays']],
            "fromDate": from_date.isoformat() if from_date else None,
            "toDate": to_date.isoformat() if to_date else None,
        }

    db.session.commit()

    return jsonify({
        "resultsPerCategory": results_per_category,
        "lastRequest": last_request.isoformat() if last_request else None,
        "availableData": available_data.isoformat() if available_data else None,
        "lastError": last_error.isoformat() if last_error else None,
        "progressEventChannel": progress_event_channel,
        "simplifiedPayroll": companies_info.simplified_annual_payroll if companies_info else False,
    })


def check_input(data):
    """Checks if the queries are valid"""
    errors = []

    if not 'categories' in data or len(data['categories']) > 1:
        return

    if 'fromDate' in data:
        if not data['fromDate']:
            errors.append('From date is required')
        else:
            data['fromDate'] = val.check_date(errors, data['fromDate'], 'From')
    if 'toDate' in data:
        if not data['toDate']:
            errors.append('To date is required')
        else:
            data['toDate'] = val.check_date(errors, data['toDate'], 'To')

    if errors:
        raise InvalidUsage(errors)
