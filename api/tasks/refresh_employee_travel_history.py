"""Background task responsible for processing traveller data"""

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from flask_sse import sse
from celery_app import app as celery
from models.storage import db, joinedload
from models.customers import Customer
from models.employees import HomeCountryClarification, InboundAssumptionConfirmation, \
                             BorderCrossTimeClarification, OutboundAssumptionConfirmation
from models.employee_spreadsheets import EmployeeSpreadsheet
# pylint: disable=W0611
from models.travels import Travel, IgnoredEmployee, IgnoredTrip
from models.traveller_data import TravellerData
from models.traveller_data_periods import TravellerDataPeriod
from models.assumptions import Assumptions
from models.treaties import Treaty
from models.employee_travel_history import EmployeeTravelHistory
from models.report_periods import ReportPeriod
from models.users import User
import processing.employee_travel_history
import processing.employees
import processing.trips


ONE_DAY = relativedelta(days=1)
ONE_MONTH = relativedelta(months=1)


def schedule(customer_id):
    """Updates the employee travel history version column
    and delays a celery task to actually calculate
    the history in the background"""
    now = datetime.now()
    customer = Customer.query.get(customer_id)
    customer.last_travel_history_request = now
    db.session.commit()
    execute.delay(customer_id, now)


def _all_tax_months_between(from_date, to_date):
    """Generate a list of tax months tuples (start, end - 1)
    between from_date and to_date"""
    tax_months = []
    start = date(from_date.year, from_date.month, 6)
    if from_date.day < 6:
        start -= ONE_MONTH
    while start <= to_date:
        tax_months.append({'from_date': start, 'to_date': start + ONE_MONTH - ONE_DAY})
        start += ONE_MONTH
    return tax_months


@celery.task
def execute(customer_id, version_ts):
    """Called whenever a relevant entity is changed by
    a client. Processes all employee travel history and
    stores the result in the database"""

    try:

        sse_channel = 'travel-history-processing-progress-{0}-{1}'.format(customer_id, version_ts)

        # collect relevant data
        sse.publish({'status': 'Collecting relevant data...',
                     'progress': 0}, channel=sse_channel)
        employee_spreadsheet = EmployeeSpreadsheet.query \
                                                .options(joinedload('employees')) \
                                                .options(joinedload('employees.arrangements')) \
                                                .filter_by(customer_id=customer_id, active=True) \
                                                .first()
        raw_employees_data = employee_spreadsheet.employees if employee_spreadsheet else []
        raw_travel_data = Travel.query \
                                .yield_per(1000) \
                                .join(Travel.traveller_data) \
                                .join(TravellerData.traveller_data_periods) \
                                .filter(TravellerDataPeriod.customer_id == customer_id) \
                                .all()
        raw_travel_data = sorted(raw_travel_data, key=lambda x: x.effective_employee_id)
        assumptions = Assumptions.query.get(customer_id)
        treaties = Treaty.query.all()
        home_country_clarifications = HomeCountryClarification.query \
                                                              .filter_by(customer_id=customer_id) \
                                                              .all()
        inb_assu_confirmations = InboundAssumptionConfirmation.query \
                                                              .filter_by(customer_id=customer_id) \
                                                              .filter_by(confirmed=False) \
                                                              .all()
        out_assu_conf = OutboundAssumptionConfirmation.query \
                                                      .filter_by(customer_id=customer_id) \
                                                      .filter_by(confirmed=False) \
                                                      .all()
        border_cross_clarifs = BorderCrossTimeClarification.query \
                                                           .filter_by(customer_id=customer_id) \
                                                           .all()
        ignored_employees = IgnoredEmployee.query \
                                           .filter_by(customer_id=customer_id) \
                                           .all()
        ignored_trips = IgnoredTrip.query \
                                   .filter_by(customer_id=customer_id) \
                                   .all()

        # process it
        sse.publish({'status': 'Processing employees...',
                     'progress': 10}, channel=sse_channel)

        employees = processing.employees.process(raw_employees_data)
        sse.publish({'status': 'Processing trips...',
                     'progress': 20}, channel=sse_channel)

        trips = processing.trips.process(raw_travel_data, border_cross_clarifs,
                                         ignored_employees, ignored_trips)
        sse.publish({'status': 'Generating employee travel history...',
                     'progress': 30}, channel=sse_channel)
        emp_travel_history = processing.employee_travel_history.process(employees, trips,
                                                                        home_country_clarifications,
                                                                        assumptions, treaties,
                                                                        inb_assu_confirmations,
                                                                        out_assu_conf)

        # we DONT want to modify any of the processed state,
        # only the calculated values
        db.session.expunge_all()

        # store results
        sse.publish({'status': 'Storing results...', 'progress': 90}, channel=sse_channel)
        if emp_travel_history:
            for row in emp_travel_history:
                row['customer_id'] = customer_id
                row['version_ts'] = version_ts
            db.session.execute(EmployeeTravelHistory.__table__.insert(), emp_travel_history)

        # invalidate all current report periods so the user can see
        # the most recent data
        report_period_ids = db.session.query(ReportPeriod.id) \
                                      .join('user') \
                                      .filter(User.customer_id == customer_id)
        ReportPeriod.query \
                    .filter(ReportPeriod.id.in_(report_period_ids)) \
                    .delete(synchronize_session=False)

        parsed_version_ts = datetime.strptime(version_ts, "%Y-%m-%dT%H:%M:%S.%f")
        customer = Customer.query.get(customer_id)
        if not customer.last_available_travel_history or \
           customer.last_available_travel_history < parsed_version_ts:
            customer.last_available_travel_history = parsed_version_ts

        db.session.commit()
        sse.publish({'status': 'Finished!', 'progress': 100}, channel=sse_channel)

    except:
        db.session.rollback()

        parsed_version_ts = datetime.strptime(version_ts, "%Y-%m-%dT%H:%M:%S.%f")
        customer = Customer.query.get(customer_id)
        if not customer.last_travel_history_error or \
           customer.last_travel_history_error < parsed_version_ts:
            customer.last_travel_history_error = parsed_version_ts
        db.session.commit()
        sse.publish({'status': 'Finished with errors!', 'progress': 100}, channel=sse_channel)

        raise
