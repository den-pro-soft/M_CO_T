"""Employees REST resource"""

from uuid import uuid4
from datetime import datetime
from collections import defaultdict
from io import BytesIO
import xlrd
from flask import Blueprint, request, jsonify, send_file
import security
from error_handling import InvalidUsage
import spreadsheets
import aws
import validation as val
from models.storage import db, joinedload
from models.companies_infos import CompaniesInfo
from models.employee_spreadsheets import EmployeeSpreadsheet
from models.employees import Employee, EmployeeArrangement
from models.travels import IgnoredEmployee
import tasks.refresh_employee_travel_history
# pylint: disable=C0103
bp = Blueprint('employees', __name__)


KNOWN_EMPLOYEE_CATEGORIES = {
    'UK Employees': 1,
    'Overseas Branch Employees': 2,
    'UK Expatriate Employees': 3,
    'NT code - STA Employees': 4,
}


@bp.route('', methods=['GET'])
def fetch():
    """Returns data about employees"""
    user = security.authorize(request)

    companies_infos = CompaniesInfo.query.filter_by(customer_id=user.customer.id).first()
    spreadsheet = EmployeeSpreadsheet.query.filter_by(customer_id=user.customer.id)

    unsaved = request.args.get('unsaved') == 'true'
    if not unsaved:
        spreadsheet = spreadsheet.filter_by(active=True)

    spreadsheet = spreadsheet.order_by(EmployeeSpreadsheet.upload_date.desc()).first()

    return jsonify({
        "id": spreadsheet.id if spreadsheet else None,
        "dateOfLastUpload": spreadsheet.upload_date.isoformat() if spreadsheet else None,
        "fileName": spreadsheet.file_name if spreadsheet else None,
        "ukEmployees": count_employees(spreadsheet, 1),
        "overseasBranchEmployees": count_employees(spreadsheet, 2),
        "ukExpatriates": count_employees(spreadsheet, 3),
        "ntStaEmployees": count_employees(spreadsheet, 4),
        "overseasBranchEmployeesEnabled": companies_infos and companies_infos.branches_overseas,
        "ukExpatriatesEnabled": companies_infos and companies_infos.employees_on_assignment_uk,
        "ntStaEmployeesEnabled": companies_infos and companies_infos.any_non_taxable_employees,
        "active": spreadsheet.active if spreadsheet else True,
    })


@bp.route('/details', methods=['GET'])
def fetch_employees():
    """Fetches all employees from a spreadsheet"""

    user = security.authorize(request)

    spreadsheet = EmployeeSpreadsheet.query.filter_by(customer_id=user.customer.id)
    unsaved = request.args.get('unsaved') == 'true'
    if not unsaved:
        spreadsheet = spreadsheet.filter_by(active=True)

    spreadsheet = spreadsheet.order_by(EmployeeSpreadsheet.upload_date.desc()).first()
    if spreadsheet:
        employees = Employee.query \
                            .options(joinedload('arrangements')) \
                            .filter_by(employee_spreadsheet_id=spreadsheet.id) \
                            .order_by(Employee.name, Employee.employee_id) \
                            .all()
    else:
        employees = []
    duplicated_ids = Employee.duplicated_ids(employees)
    mapper = lambda employee: convert_employee(employee, duplicated_ids)
    return jsonify(list(map(mapper, employees)))


def convert_employee(employee, duplicated_ids):
    """Creates a dict representation of an employee"""
    sorted_arrangements = employee.sorted_arrangements()
    arrangements = list(map(convert_arrangement, sorted_arrangements))
    return {
        "id": employee.id,
        "name": employee.name,
        "employeeId": employee.employee_id,
        "duplicated": is_duplicated(arrangements),
        "duplicatedId": employee.effective_id in duplicated_ids,
        "arrangements": arrangements
    }


def convert_arrangement(arrangement):
    """Creates a dict representation of an arrangement"""
    return {
        "category": arrangement.category,
        "effectiveFrom": arrangement.effective_from.isoformat()
                         if arrangement.effective_from else None,
        "effectiveTo": arrangement.effective_to.isoformat()
                       if arrangement.effective_to else None,
    }


def is_duplicated(arrangements):
    """Checks if an employee is currently duplicated across
    different work arrangements without proper period info"""
    return EmployeeArrangement.has_duplication(arrangements)


def count_employees(spreadsheet, category):
    """Counts spreadsheet employees by category"""
    if not spreadsheet:
        return 0
    return EmployeeArrangement.query \
                              .join(EmployeeArrangement.employee, aliased=True) \
                              .filter(Employee.employee_spreadsheet_id == spreadsheet.id) \
                              .filter(EmployeeArrangement.category == category) \
                              .count()


@bp.route('/data-template', methods=['GET'])
def generate_data_template():
    """Generates the template spreadsheet based on
    answers on the cmpany page"""
    user = security.authorize(request)
    companies_infos = CompaniesInfo.query.filter_by(customer_id=user.customer.id).first()
    book = spreadsheets.open_workbook_template('Employees.xlsx')

    if companies_infos:
        if not companies_infos.any_non_taxable_employees:
            spreadsheets.remove_worksheet(book, 'NT code - STA Employees')
        if not companies_infos.employees_on_assignment_uk:
            spreadsheets.remove_worksheet(book, 'UK Expatriate Employees')
        if not companies_infos.branches_overseas:
            spreadsheets.remove_worksheet(book, 'Overseas Branch Employees')

    stream = spreadsheets.get_bytes(book)
    response = send_file(stream, attachment_filename='Employees.xlsx')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Content-Disposition'] = 'attachment; filename=Employees.xlsx'
    return response


def disable_current_spreadsheets(customer_id):
    """Disable spreadsheets currently marked as active for the user"""
    current = EmployeeSpreadsheet.query.filter_by(customer_id=customer_id, active=True).all()
    for active_spreadsheet in current:
        active_spreadsheet.active = False


@bp.route('/<spreadsheet_id>/activate', methods=['POST'])
def activate(spreadsheet_id):
    """Activates an unsaved spreadsheet"""
    user = security.authorize(request)
    disable_current_spreadsheets(user.customer.id)
    spreadsheet = EmployeeSpreadsheet.query \
                                     .options(joinedload('employees')) \
                                     .options(joinedload('employees.arrangements')) \
                                     .filter(EmployeeSpreadsheet.customer_id == user.customer.id) \
                                     .filter(EmployeeSpreadsheet.id == spreadsheet_id) \
                                     .first()
    if spreadsheet is None:
        raise InvalidUsage('Spreadsheet not found')
    spreadsheet.active = True

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    check_employee_input(data)

    found_any_duplication = process_employee_changes(spreadsheet, data)

    db.session.commit()

    tasks.refresh_employee_travel_history.schedule(user.customer.id)

    return jsonify({
        "foundAnyDuplication": found_any_duplication,
    })


def check_employee_input(data):
    """Checks if the employee list input is valid"""
    errors = []

    employees = []
    if 'additions' in data and isinstance(data['additions'], list):
        employees += data['additions']
    if 'changes' in data and isinstance(data['changes'], list):
        employees += data['changes']

    for idx, employee in enumerate(employees):
        error_prefix = 'Employee #{0}'.format(idx + 1)
        empty_name = 'name' not in employee or not employee['name']
        empty_emp_id = 'employeeId' not in employee or not employee['employeeId']
        if empty_name and empty_emp_id:
            errors.append('{0}: Name or Id is required'.format(error_prefix))
        check_employee_arrangements(errors, error_prefix, employee)

    if errors:
        raise InvalidUsage(errors)


def check_employee_arrangements(errors, employee_error_prefix, employee):
    """Checks all the employee arrangements"""
    if 'arrangements' in employee and isinstance(employee['arrangements'], list):
        last_eff_date = None
        for idx, arrangement in enumerate(employee['arrangements']):
            error_prefix = "{0} - Arrangement #{1}".format(employee_error_prefix, idx + 1)
            empty_category = 'category' not in arrangement or not arrangement['category']
            if empty_category:
                errors.append('{0}: Category is required'.format(error_prefix))
            eff_from = None
            empty_eff_from = 'effectiveFrom' not in arrangement or not arrangement['effectiveFrom']
            if not empty_eff_from:
                eff_from = val.check_date(errors, arrangement['effectiveFrom'],
                                          '{0}: Effective From'.format(error_prefix))
            eff_to = None
            empty_eff_to = 'effectiveTo' not in arrangement or not arrangement['effectiveTo']
            if not empty_eff_to:
                eff_to = val.check_date(errors, arrangement['effectiveTo'],
                                        '{0}: Effective To'.format(error_prefix))
            if eff_from and eff_to and eff_to < eff_from:
                errors.append('{0}: Effective To must be after Effective From'
                              .format(error_prefix))
            if last_eff_date:
                if eff_from and last_eff_date > eff_from:
                    errors.append('{0}: Effective From must be after previous arrangements'
                                  .format(error_prefix))
                elif eff_to and last_eff_date > eff_to:
                    errors.append('{0}: Effective To must be after previous arrangements'
                                  .format(error_prefix))
            last_eff_date = eff_to if eff_to else eff_from if eff_from else last_eff_date


def process_employee_changes(spreadsheet, data):
    """Apply employee changes, additions and removals. Returns
    a boolean indicating if any merging ocurred (because of duplications)"""

    if 'removals' in data and isinstance(data['removals'], list):
        spreadsheet.employees = list(filter(lambda em: str(em.id) not in data['removals'],
                                            spreadsheet.employees))

    remaining_employees = {str(x.id): x for x in spreadsheet.employees}

    if 'additions' in data and isinstance(data['additions'], list):
        for employee in data['additions']:
            spreadsheet.employees.append(Employee(employee['id'],
                                                  spreadsheet.id,
                                                  employee['name'],
                                                  employee['employeeId'],
                                                  process_arrangements(employee)))

    if 'changes' in data and isinstance(data['changes'], list):
        for employee in data['changes']:
            existing_employee = remaining_employees[employee['id']]
            existing_employee.name = employee['name']
            existing_employee.employee_id = employee['employeeId']
            existing_employee.arrangements = process_arrangements(employee)

    # merge duplicates
    found_any_duplication = False
    employees_by_key = defaultdict(list)
    for employee in spreadsheet.employees:
        key = (employee.name, employee.employee_id)
        employees_by_key[key].append(employee)
    for _, employees in employees_by_key.items():
        if len(employees) > 1:
            found_any_duplication = True
            first = employees[0]
            first_arrangements = [str(arr.category) for arr in first.arrangements]
            for duplicate in employees[1:]:
                for arr in duplicate.arrangements:
                    if str(arr.category) not in first_arrangements:
                        first.arrangements.append(EmployeeArrangement(uuid4(),
                                                                      first.id,
                                                                      arr.category,
                                                                      None,
                                                                      None))
                    duplicate.arrangements.remove(arr)
                spreadsheet.employees.remove(duplicate)
    return found_any_duplication


def process_arrangements(employee):
    """Process arrangement input data into the
    corresponding model objects"""
    return list(map(lambda arr: EmployeeArrangement(uuid4(),
                                                    employee['id'],
                                                    arr['category'],
                                                    arr['effectiveFrom'],
                                                    arr['effectiveTo']),
                    employee['arrangements']))


@bp.route('/deactivate-current', methods=['POST'])
def deactivate_current():
    """Deactivates current spreadsheet"""
    user = security.authorize(request)
    disable_current_spreadsheets(user.customer.id)
    db.session.commit()
    tasks.refresh_employee_travel_history.schedule(user.customer.id)
    return ('', 204)


@bp.route('/ignored', methods=['POST'])
def ignore_employees():
    """Ignores multiple employees"""
    user = security.authorize(request)

    data = request.get_json()
    if data is None or not isinstance(data, list):
        raise InvalidUsage('Invalid data')

    for employee in data:
        db.session.add(IgnoredEmployee(pk=uuid4(),
                                       customer_id=user.customer.id,
                                       traveller_name=employee['travellerName'],
                                       employee_id=employee['employeeId']))
    db.session.commit()
    tasks.refresh_employee_travel_history.schedule(user.customer.id)
    return ('', 204)


@bp.route('', methods=['POST'])
def upload():
    """Receives a upload for processing"""
    user = security.authorize(request)

    if 'file' not in request.files:
        raise InvalidUsage('Missing file data')

    uploaded_file = request.files['file']
    data = uploaded_file.read()

    with BytesIO(data) as stream:
        upload_key = aws.s3upload(stream)

    try:

        book = xlrd.open_workbook(file_contents=data)

        employee_spreadsheet_id = uuid4()

        # row key is a tuple like (name, employee_id)
        employees = defaultdict(set)

        for sheet in book.sheets():
            if sheet.name not in KNOWN_EMPLOYEE_CATEGORIES:
                continue
            for row in range(1, sheet.nrows):
                employee_name = spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=0))
                employee_id = spreadsheets.parse_text(sheet.cell_value(rowx=row, colx=1))
                if employee_name or employee_id:
                    category = KNOWN_EMPLOYEE_CATEGORIES[sheet.name]
                    employees[(employee_name, employee_id)].add(category)

    except xlrd.XLRDError:
        raise InvalidUsage('Unsupported spreadsheet. Please check the uploaded file.')

    emp_ssheet = dict(id=employee_spreadsheet_id,
                      customer_id=user.customer.id,
                      upload_date=datetime.now(),
                      active=False,
                      file_name=uploaded_file.filename,
                      upload_key=upload_key)

    employee_rows = []
    employee_arrangement_rows = []
    for (emp_name, emp_id), categories in employees.items():
        employee_row_id = uuid4()
        employee_rows.append(dict(id=employee_row_id,
                                  employee_spreadsheet_id=employee_spreadsheet_id,
                                  name=emp_name,
                                  employee_id=emp_id))
        for category in categories:
            employee_arrangement_rows.append(dict(id=uuid4(),
                                                  employee_id=employee_row_id,
                                                  category=category))

    db.session.execute(EmployeeSpreadsheet.__table__.insert(), emp_ssheet)
    if employee_rows:
        db.session.execute(Employee.__table__.insert(), employee_rows)
    if employee_arrangement_rows:
        db.session.execute(EmployeeArrangement.__table__.insert(), employee_arrangement_rows)
    db.session.commit()

    return ('', 204)


@bp.route('/<spreadsheet_id>/download', methods=['GET'])
def download(spreadsheet_id):
    """Downloads the spreadsheet data"""
    user = security.authorize(request)
    employee_spreadsheet = EmployeeSpreadsheet.query.get(spreadsheet_id)
    if not employee_spreadsheet:
        raise InvalidUsage('Employee Spreadsheet not found')
    elif employee_spreadsheet.customer_id != user.customer.id:
        raise InvalidUsage('Access denied')
    data = aws.s3download(employee_spreadsheet.upload_key)
    return send_file(data, attachment_filename=employee_spreadsheet.file_name)
