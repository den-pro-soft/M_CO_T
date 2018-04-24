"""REST resource responsible for traveller data spreadsheets"""


from datetime import datetime, time
from uuid import uuid4, UUID
from io import BytesIO
import xlrd
from flask import Blueprint, request, jsonify, send_file
from flask_sse import sse
import security
import aws
import spreadsheets
import validation as val
from error_handling import InvalidUsage
from models.storage import db
from models.traveller_data import TravellerData
from models.travels import Travel, TRAVELLER_DATA_ERROR_CODES, TravellerDataError
from models.traveller_data_periods import TravellerDataPeriod
from models.countries import Country, CountryAlias
import tasks.refresh_employee_travel_history
# pylint: disable=C0103
bp = Blueprint('traveller-data', __name__)


@bp.route('', methods=['POST'])
def upload():
    """Receives a upload for processing"""
    user = security.authorize(request)

    if 'file' not in request.files:
        raise InvalidUsage('Missing file data')

    if 'id' not in request.form:
        raise InvalidUsage('Missing request id')
    upload_id = UUID(request.form['id'])
    sse_channel = 'upload-progress-{0}'.format(upload_id)

    from_date = None
    if 'from' in request.form:
        from_date = val.check_date([], request.form['from'], '')
        from_date = from_date.date() if from_date else None

    to_date = None
    if 'to' in request.form:
        to_date = val.check_date([], request.form['to'], '')
        to_date = to_date.date() if to_date else None

    uploaded_file = request.files['file']
    data = uploaded_file.read()

    sse.publish({'status': 'Storing a copy on our servers...'}, channel=sse_channel)

    with BytesIO(data) as stream:
        upload_key = aws.s3upload(stream)

    sse.publish({'status': 'Processing traveller data...', 'progress': 0}, channel=sse_channel)

    countries = Country.query.all()
    country_aliases = CountryAlias.query.all()

    try:

        book = xlrd.open_workbook(file_contents=data)

        def generate_rows():
            """Process the spreadsheet generating rows"""
            if 'Traveller Data' not in book.sheet_names():
                raise InvalidUsage('No "Traveller Data" worksheet found in this workbook')
            sheet = book.sheet_by_name('Traveller Data')
            if sheet.ncols < 20:
                raise InvalidUsage('Invalid number of columns ' +
                                   'in the spreadsheet (expected: 20).')
            for row in range(1, sheet.nrows):
                travel = create_travel_record(sheet, row, countries, country_aliases)
                if travel:
                    yield travel

        rows = generate_rows()
        total_rows = sum([sheet.nrows - 1 for sheet in book.sheets()])

        traveller_data_id = uuid4()
        upload_date = datetime.now()
        traveller_data = dict(id=traveller_data_id,
                              customer_id=user.customer.id,
                              upload_date=upload_date,
                              upload_key=upload_key,
                              filename=uploaded_file.filename,
                              valid=False)

        db.session.execute(TravellerData.__table__.insert(), traveller_data)

        # count trips before or after the period if applicable
        trips_before_period = 0
        trips_after_period = 0

        travel_count = 0
        row_count = 0
        invalid_trips_count = 0
        error_count = 0
        travel_rows = []
        error_rows = []
        for row in rows:
            row_count += 1
            if row['errors'] and row['ticket_type'] != 'Refund':
                invalid_trips_count += 1
                error_count += len(row['errors'])
            row['id'] = uuid4()
            row['traveller_data_id'] = traveller_data_id
            travel_rows.append(row)
            for error in row['errors']:
                error_rows.append({'travel_id': row['id'], 'error_code': error})
            if row['ticket_type'] != 'Refund':
                travel_count += 1
                if from_date:
                    if row['departure_date'] and row['departure_date'] < from_date:
                        trips_before_period += 1
                    elif row['arrival_date'] and row['arrival_date'] < from_date:
                        trips_before_period += 1
                if to_date:
                    if row['departure_date'] and row['departure_date'] > to_date:
                        trips_after_period += 1
                    elif row['arrival_date'] and row['arrival_date'] > to_date:
                        trips_after_period += 1
            if len(travel_rows) >= 1000:
                progress_status = 'Processing traveller data ' + \
                                  '({0} rows processed)...'.format(row_count)
                sse.publish({'status': progress_status,
                             'progress': row_count/total_rows*100}, channel=sse_channel)
                db.session.execute(Travel.__table__.insert(), travel_rows)
                travel_rows.clear()
                if error_rows:
                    db.session.execute(TravellerDataError.__table__.insert(), error_rows)
                    error_rows.clear()

        if travel_rows:
            db.session.execute(Travel.__table__.insert(), travel_rows)
        if error_rows:
            db.session.execute(TravellerDataError.__table__.insert(), error_rows)

        if error_count > 0:
            query = TravellerData.__table__.update().where(TravellerData.id == traveller_data_id)
            db.session.execute(query, {'valid': False})

        sse.publish({'status': 'Done!', 'progress': 100}, channel=sse_channel)

        db.session.commit()

    except xlrd.XLRDError:
        raise InvalidUsage('Unsupported spreadsheet. Please check the uploaded file.')

    return jsonify({
        "entryCount": travel_count,
        "id": traveller_data_id,
        "filename": uploaded_file.filename,
        "dateUploaded": upload_date.isoformat(),
        "errorCount": error_count,
        "tripsBeforePeriod": trips_before_period,
        "tripsAfterPeriod": trips_after_period,
        "invalidCount": invalid_trips_count,
        "outsidePeriodCount": trips_before_period + trips_after_period,
    })


@bp.route('/<traveller_data_id>', methods=['GET'])
def download(traveller_data_id):
    """Downloads the spreadsheet data"""
    user = security.authorize(request)
    traveller_data = TravellerData.query.get(traveller_data_id)
    if not traveller_data:
        raise InvalidUsage('Traveller data not found')
    elif traveller_data.customer_id != user.customer.id:
        raise InvalidUsage('Access denied')
    data = aws.s3download(traveller_data.upload_key)
    return send_file(data, attachment_filename=traveller_data.filename)


@bp.route('/periods', methods=['PUT'])
def save_periods():
    """Updates traveller data periods"""
    user = security.authorize(request)

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    periods = data

    check_periods_input(periods)

    TravellerDataPeriod.query.filter_by(customer_id=user.customer.id).delete()

    for period in periods:
        has_traveller_data = 'travellerData' in period and period['travellerData']
        traveller_data_id = period['travellerData']['id'] if has_traveller_data else None
        db.session.add(TravellerDataPeriod(pk=uuid4(),
                                           customer_id=user.customer.id,
                                           from_date=period['from'],
                                           to_date=period['to'],
                                           traveller_data_id=traveller_data_id))

    db.session.commit()
    tasks.refresh_employee_travel_history.schedule(user.customer.id)
    return ('', 204)


@bp.route('/periods', methods=['POST'])
def add_period():
    """Save a new traveller data period"""
    user = security.authorize(request)

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    period = data

    check_periods_input([period])

    has_traveller_data = 'travellerData' in period and period['travellerData']
    traveller_data_id = period['travellerData']['id'] if has_traveller_data else None
    db.session.add(TravellerDataPeriod(pk=uuid4(),
                                       customer_id=user.customer.id,
                                       from_date=period['from'],
                                       to_date=period['to'],
                                       traveller_data_id=traveller_data_id))

    db.session.commit()
    tasks.refresh_employee_travel_history.schedule(user.customer.id)
    return ('', 204)


@bp.route('/periods', methods=['GET'])
def fetch_periods():
    """Returns data about traveller data periods"""
    user = security.authorize(request)
    periods = TravellerDataPeriod.query \
                                 .join(TravellerDataPeriod.traveller_data) \
                                 .filter_by(customer_id=user.customer.id) \
                                 .order_by(TravellerData.upload_date.desc()) \
                                 .all()
    return jsonify(list(map(lambda period: {
        "id": period.id,
        "from": period.from_date.isoformat(),
        "to": period.to_date.isoformat(),
        "travellerData": {
            "id": period.traveller_data.id,
            "entryCount": count_travels(period.traveller_data.id),
            "filename": period.traveller_data.filename,
            "dateUploaded": period.traveller_data.upload_date.isoformat(),
            "valid": period.traveller_data.valid,
            "invalidCount": count_invalid_travels(period.traveller_data.id),
            "outsidePeriodCount": count_travels_outside_period(period.id),
        } if period.traveller_data else None,
    }, periods)))


def count_travels_outside_period(period_id):
    """Count travels outside period from/to date"""

    has_departure_date = Travel.departure_date != None
    has_arrival_date = Travel.arrival_date != None
    departure_date_after_to_date = Travel.departure_date > TravellerDataPeriod.to_date
    arrival_date_after_to_date = Travel.arrival_date > TravellerDataPeriod.to_date
    arrival_date_before_from = Travel.arrival_date < TravellerDataPeriod.from_date
    departure_date_before_from = Travel.departure_date < TravellerDataPeriod.from_date

    after_to = (has_departure_date & departure_date_after_to_date) | \
               (has_arrival_date & arrival_date_after_to_date)
    before_from = (has_arrival_date & arrival_date_before_from) | \
                  (has_departure_date & departure_date_before_from)

    return TravellerDataPeriod.query \
                              .join(TravellerDataPeriod.traveller_data) \
                              .join(TravellerData.travels) \
                              .filter(TravellerDataPeriod.id == period_id) \
                              .filter(Travel.ticket_type != 'Refund') \
                              .filter(after_to | before_from) \
                              .count()


def count_invalid_travels(traveller_data_id):
    """Count invalid/incomplete travels of a spreadsheet"""
    return Travel.query \
                 .filter_by(traveller_data_id=traveller_data_id, invalid=True) \
                 .filter(Travel.ticket_type != 'Refund') \
                 .count()


def count_travels(traveller_data_id):
    """Counts travels related to a traveller data"""
    return Travel.query \
                 .filter_by(traveller_data_id=traveller_data_id) \
                 .filter(Travel.ticket_type != 'Refund') \
                 .count()


def check_country(subject, error_code, errors, countries, country_aliases):
    """Verifies if a country is valid"""
    if not subject:
        return None
    matches = [x for x in countries if x.code == subject or x.name.upper() == subject]
    if matches:
        return matches[0].code
    aliases = [x for x in country_aliases if x.alias.upper() == subject]
    if aliases:
        return aliases[0].code
    if error_code:
        errors.append(TRAVELLER_DATA_ERROR_CODES[error_code])
    return None


def create_travel_record(sheet, row, countries, country_aliases):
    """Converts a traveller data spreadsheet row
    to a Travel record dictionary"""

    traveller_name = spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=0))
    employee_id = spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=1))

    if not traveller_name and not employee_id:
        return None

    errors = []

    # should fail silently (that is why we pass None as error_code,
    # the proper reporting will occur on additional clarifications
    employee_country = check_country(sheet.cell_value(rowx=row, colx=3).upper(),
                                     None,
                                     errors, countries, country_aliases)

    booking_date = None
    try:
        booking_date = spreadsheets.read_date(sheet, row, colx=5)
    except ValueError:
        errors.append(TRAVELLER_DATA_ERROR_CODES['INVALID_BOOKING_DATE'])

    origin_country = check_country(sheet.cell_value(rowx=row, colx=11).upper(),
                                   'INVALID_ORIGIN_COUNTRY',
                                   errors, countries, country_aliases)

    destination_country = check_country(sheet.cell_value(rowx=row, colx=13).upper(),
                                        'INVALID_DESTINATION_COUNTRY',
                                        errors, countries, country_aliases)

    departure_date = None
    try:
        departure_date = spreadsheets.read_date(sheet, row, colx=16)
    except ValueError:
        errors.append(TRAVELLER_DATA_ERROR_CODES['INVALID_DEPARTURE_DATE'])

    departure_time = None
    try:
        departure_time = spreadsheets.read_time(sheet, row, colx=17)
        if not departure_time:
            departure_time = time(0, 0)
    except ValueError:
        departure_time = time(0, 0)

    arrival_date = None
    try:
        arrival_date = spreadsheets.read_date(sheet, row, colx=18)
    except ValueError:
        errors.append(TRAVELLER_DATA_ERROR_CODES['INVALID_ARRIVAL_DATE'])

    arrival_time = None
    try:
        arrival_time = spreadsheets.read_time(sheet, row, colx=19)
        if not arrival_time:
            arrival_time = time(0, 0)
    except ValueError:
        arrival_time = time(0, 0)

    incomplete = not departure_date \
                 or not arrival_date \
                 or not origin_country \
                 or not destination_country

    if not errors and incomplete:
        errors.append(TRAVELLER_DATA_ERROR_CODES['INCOMPLETE'])

    border_cross = None
    if departure_date and origin_country == 'GBR':
        departure_time_part = departure_time.time() \
                              if isinstance(departure_time, datetime) else departure_time
        border_cross = datetime.combine(departure_date, departure_time_part)
    elif arrival_date and origin_country != 'GBR':
        arrival_time_part = arrival_time.time() \
                            if isinstance(arrival_time, datetime) else arrival_time
        border_cross = datetime.combine(arrival_date, arrival_time_part)

    return {
        "traveller_name": traveller_name,
        "employee_id": employee_id,
        "employing_entity": spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=2)),
        "employee_country": employee_country,
        "au": spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=4)),
        "booking_date": booking_date,
        "record_locator": spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=6)),
        "ticket_no": spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=7)),
        "ticket_type": spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=8)),
        "segment_no": spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=9)),
        "calculated_seg_no": spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=10)),
        "origin_country_name": origin_country,
        "origin_airport_code": spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=12)),
        "destination_country_name": destination_country,
        "destination_airport_code": spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=14)),
        "routing_airports": spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=15)),
        "departure_date": departure_date,
        "departure_time": departure_time,
        "arrival_date": arrival_date,
        "arrival_time": arrival_time,
        "errors": errors,
        "invalid": len(errors) > 0,
        "row": row + 1,
        "border_cross": border_cross,
    }

def check_periods_input(periods):
    """Checks the validity of periods input"""
    errors = []

    for period in periods:

        period_id = period['travellerData']['filename'] \
                    if 'travellerData' in period and period['travellerData'] else 'New Period'
        error_prefix = '{0}:'.format(period_id)
        from_date = None
        to_date = None

        if 'from' not in period or not period['from']:
            errors.append('{0} From date is required'.format(error_prefix))
        else:
            from_date = val.check_date(errors, period['from'], '{0} From date'.format(error_prefix))

        if 'to' not in period or not period['to']:
            errors.append('{0} To date is required'.format(error_prefix))
        else:
            to_date = val.check_date(errors, period['to'], '{0} To date'.format(error_prefix))

        if from_date and to_date:
            if to_date < from_date:
                errors.append('{0} To date must be after From date'.format(error_prefix))

        if 'travellerData' not in period or not period['travellerData']:
            errors.append('{0} please upload the traveller data'.format(error_prefix))

    if errors:
        raise InvalidUsage(errors)
