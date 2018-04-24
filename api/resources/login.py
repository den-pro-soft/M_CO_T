"""Login REST resource"""

from uuid import uuid4
from flask import Blueprint, request, jsonify
from error_handling import InvalidUsage
import security
from models.storage import db, joinedload
from models.users import User
from models.auth_tokens import AuthToken
from models.applications import MINTAX_BUSINESS_TRAVELLERS_ID
# pylint: disable=C0103
bp = Blueprint('login', __name__)


ACCOUNT_BLOCKED_MESSAGE = 'Account blocked. Please recover your password ' + \
                          'using the Forgot My Password feature or contact ' + \
                          'E-Tax Consulting for support.'

@bp.route('', methods=['POST'])
def login():
    """Receives a login attempt, validates
    it and generates an auth token"""

    attempt = request.get_json()
    if attempt is None:
        raise InvalidUsage('Invalid data')

    errors = []
    if not 'email' in attempt or not attempt['email']:
        errors.append('E-mail is required')
    if not 'password' in attempt or not attempt['password']:
        errors.append('Password is required')
    if errors:
        raise InvalidUsage(errors)

    if not 'captchaToken' in attempt or not attempt['captchaToken']:
        raise InvalidUsage('Please provide a captcha token')
    elif not security.check_captcha(attempt['captchaToken']):
        raise InvalidUsage('Invalid captcha token')

   
    user = User.query \
               .options(joinedload('customer.applications')) \
               .filter_by(email=attempt['email']) \
               .first()
    if not user:
        raise InvalidUsage('Invalid e-mail or password')

    if user.unsucessful_login_attemps >= 3:
        raise InvalidUsage(ACCOUNT_BLOCKED_MESSAGE)

    hashed_password = security.strong_hash(attempt['password'])
    if not hashed_password == user.password:
        user.unsucessful_login_attemps += 1
        db.session.commit()
        if user.unsucessful_login_attemps >= 3:
            raise InvalidUsage(ACCOUNT_BLOCKED_MESSAGE)
        else:
            raise InvalidUsage('Invalid e-mail or password')

    if not user.active:
        raise InvalidUsage('Disabled user account')
    if not user.customer.active:
        raise InvalidUsage('Disabled customer account')
    if not MINTAX_BUSINESS_TRAVELLERS_ID in [app.id for app in user.customer.applications]:
        raise InvalidUsage('Customer does not have access to this application')

    auth_token = AuthToken(uuid4(), user)
    user.unsucessful_login_attemps = 0
    db.session.add(auth_token)
    db.session.commit()

    return jsonify({
        'authToken': auth_token.id
    })


@bp.route('/password', methods=['PUT'])
def change_password():
    """Allows the user to change their password"""
    user = security.authorize(request)

    data = request.get_json()
    if data is None:
        raise InvalidUsage('Invalid data')

    errors = []
    if not 'current' in data or not data['current']:
        errors.append('Current password is required')
    filled_new_password = 'new' in data and data['new']
    filled_password_confirmation = 'confirmation' in data and data['confirmation']
    if not filled_new_password:
        errors.append('New password is required')
    elif len(data['new']) < 8 or security.unsafe_password(data['new']):
        errors.append('Your new password should have a minimum length of 8 characters and ' +
                      'include at least 1 lowercase letter, 1 uppercase letter and 1 number')
    if not filled_password_confirmation:
        errors.append('Password confirmation is required')
    if filled_new_password and filled_password_confirmation and data['new'] != data['confirmation']:
        errors.append('Your new password and the confirmation must match')
    if errors:
        raise InvalidUsage(errors)

    hashed_password = security.strong_hash(data['current'])
    if not hashed_password == user.password:
        raise InvalidUsage('Current password is invalid')

    hashed_new_password = security.strong_hash(data['new'])
    user.password = hashed_new_password
    db.session.commit()

    return ('', 204)


@bp.route('/info', methods=['GET'])
def info():
    """Returns data regarding the attached
    auth token, like the user first name"""
    user = security.authorize(request)
    return jsonify({
        'firstName': user.firstname,
        'secondName': user.secondname or '',
        'companyName': user.customer.name or '',
        'companyAddress': user.customer.address or '',
        'contractEndDate': user.customer.contract_end_date.isoformat() \
                           if user.customer.contract_end_date else None,
        'workEmail': user.email,
        'admin': user.admin,
    })
