"""Admin REST resource"""

from uuid import uuid4
from flask import Blueprint, request, jsonify
import security
import validation as val
from error_handling import InvalidUsage
from models.storage import db, joinedload
from models.users import User
from models.customers import Customer
from models.applications import Application
# pylint: disable=C0103
bp = Blueprint('admin', __name__)


@bp.route('/users', methods=['GET'])
def fetch_users():
    """Fetches all users data"""
    security.authorize(request)
    users = User.query.order_by(User.firstname).all()
    return jsonify(list(map(lambda user: {
        "id": user.id,
        "firstName": user.firstname,
        "secondName": user.secondname,
        "email": user.email,
        "customerName": user.customer.name,
        "active": user.active,
    }, users)))


@bp.route('/customers', methods=['GET'])
def fetch_customers():
    """Fetches all customers data"""
    security.authorize(request)
    customers = Customer.query.order_by(Customer.name).all()
    return jsonify(list(map(lambda customer: {
        "id": customer.id,
        "name": customer.name,
        "active": customer.active,
        'contractEndDate': customer.contract_end_date.isoformat() \
                           if customer.contract_end_date else None,
    }, customers)))


@bp.route('/users/<requested_user_id>', methods=['GET'])
def fetch_user(requested_user_id):
    """Fetches a specific user data"""
    security.authorize(request)
    user = User.query.get(requested_user_id)
    return jsonify({
        'firstName': user.firstname,
        'secondName': user.secondname or '',
        'customerId': user.customer_id,
        'workEmail': user.email,
        'active': user.active,
        "admin": user.admin,
    })


@bp.route('/customers/<requested_customer_id>', methods=['GET'])
def fetch_customer(requested_customer_id):
    """Fetches a specific customer data"""
    security.authorize(request)
    customer = Customer.query \
                       .options(joinedload('applications')) \
                       .get(requested_customer_id)
    has_contract_end_date = customer.contract_end_date
    contract_end_date = customer.contract_end_date.isoformat() if has_contract_end_date else None
    return jsonify({
        'name': customer.name,
        'address': customer.address or '',
        'contractEndDate': contract_end_date,
        'applications': [app.id for app in customer.applications],
        'active': customer.active,
    })


@bp.route('/users', methods=['POST'])
def add_user():
    """Adds a new user"""
    security.authorize(request)

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    check_user_input(data, adding=True)

    hashed_password = security.strong_hash(data['password'])

    user = User(id=uuid4(),
                firstname=data['firstName'],
                secondname=data['secondName'] if 'secondName' in data else '',
                customer_id=data['customerId'],
                email=data['workEmail'],
                password=hashed_password,
                admin=data['admin'],
                active=data['active'],
                unsucessful_login_attemps=0)
    db.session.add(user)
    db.session.commit()

    return ('', 204)


@bp.route('/customers', methods=['POST'])
def add_customer():
    """Adds a new customer"""
    security.authorize(request)

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    check_customer_input(data)

    has_contract_end_date = 'contractEndDate' in data and data['contractEndDate']
    contract_end_date = data['contractEndDate'] if has_contract_end_date else None
    customer = Customer(id=uuid4(),
                        name=data['name'],
                        address=data['address'] if 'address' in data else '',
                        contract_end_date=contract_end_date,
                        applications=[Application.query.get(id) for id in data['applications']] \
                                     if 'applications' in data else [],
                        active=data['active'])
    db.session.add(customer)
    db.session.commit()

    return ('', 204)


@bp.route('/users/<subject_user_id>', methods=['PUT'])
def update_user(subject_user_id):
    """Updates a user"""
    security.authorize(request)

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    check_user_input(data, adding=False)

    has_contract_end_date = 'contractEndDate' in data and data['contractEndDate']
    user = User.query.get(subject_user_id)
    user.firstname = data['firstName']
    user.secondname = data['secondName'] if 'secondName' in data else ''
    user.company_name = data['companyName'] if 'companyName' in data else ''
    user.company_address = data['companyAddress'] if 'companyAddress' in data else ''
    user.contract_end_date = data['contractEndDate'] if has_contract_end_date else None
    user.email = data['workEmail']
    user.active = data['active']
    user.admin = data['admin']

    if 'password' in data and data['password']:
        hashed_password = security.strong_hash(data['password'])
        user.password = hashed_password

    db.session.commit()

    return ('', 204)


@bp.route('/customers/<subject_customer_id>', methods=['PUT'])
def update_customer(subject_customer_id):
    """Updates a customer"""
    security.authorize(request)

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    check_customer_input(data)

    has_contract_end_date = 'contractEndDate' in data and data['contractEndDate']
    customer = Customer.query \
                    .options(joinedload('applications')) \
                    .get(subject_customer_id)
    customer.name = data['name']
    customer.address = data['address'] if 'address' in data else ''
    customer.contract_end_date = data['contractEndDate'] if has_contract_end_date else None
    customer.applications = [Application.query.get(id) for id in data['applications']] \
                            if 'applications' in data else []
    customer.active = data['active']

    db.session.commit()

    return ('', 204)


@bp.route('/users/<subject_user_id>', methods=['DELETE'])
def delete_user(subject_user_id):
    """Deletes a user"""
    security.authorize(request)
    user = User.query.get(subject_user_id)
    user.active = False
    db.session.commit()
    return ('', 204)


@bp.route('/customers/<subject_customer_id>', methods=['DELETE'])
def delete_customer(subject_customer_id):
    """Deletes a customer"""
    security.authorize(request)
    customer = Customer.query.get(subject_customer_id)
    customer.active = False
    db.session.commit()
    return ('', 204)


def check_user_input(data, adding):
    """Check the validity of input data"""
    errors = []

    if adding:
        if 'customerId' not in data or not data['customerId']:
            errors.append('Customer is required')

    if 'firstName' not in data or not data['firstName']:
        errors.append('First name is required')
    elif len(data['firstName']) > 50:
        errors.append('First name should have less than or exactly 50 characters')

    if 'secondName' in data and len(data['secondName']) > 50:
        errors.append('Second name should have less than or exactly 50 characters')

    if 'companyName' in data and len(data['companyName']) > 50:
        errors.append('Company name should have less than or exactly 50 characters')

    if 'companyAddress' in data and len(data['companyAddress']) > 4000:
        errors.append('Company address should have less than or exactly 4000 characters')

    if 'contractEndDate' in data and data['contractEndDate']:
        val.check_date(errors, data['contractEndDate'], 'Contract end date')

    if 'workEmail' not in data or not data['workEmail']:
        errors.append('Work e-mail is required')
    elif len(data['workEmail']) > 500:
        errors.append('Work e-mail should have less than or exactly 50 characters')
    else:
        val.check_email(errors, data['workEmail'], 'Work e-mail')

    check_password(errors, data, adding)

    if 'active' not in data:
        errors.append('Active: missing attribute')

    if 'admin' not in data:
        errors.append('Admin: missing attribute')

    if errors:
        raise InvalidUsage(errors)


def check_password(errors, data, password_required):
    """Checks if the user informed a valid and strong password"""
    if password_required:
        if 'password' not in data or not data['password']:
            errors.append('Password is required')

    if 'password' in data and data['password']:
        if len(data['password']) < 8 or security.unsafe_password(data['password']):
            errors.append('Password should have a minimum length of 8 and include at ' +
                          'least 1 character of each of the following categories: lowercase ' +
                          'letter, uppercase letter and digit')


def check_customer_input(data):
    """Check the validity of input data"""
    errors = []

    if 'name' not in data or not data['name']:
        errors.append('Name is required')
    elif len(data['name']) > 50:
        errors.append('Name should have less than or exactly 50 characters')

    if 'address' in data and len(data['address']) > 4000:
        errors.append('Company address should have less than or exactly 4000 characters')

    if 'contractEndDate' in data and data['contractEndDate']:
        val.check_date(errors, data['contractEndDate'], 'Contract end date')

    if 'active' not in data:
        errors.append('Active: missing attribute')

    if errors:
        raise InvalidUsage(errors)
