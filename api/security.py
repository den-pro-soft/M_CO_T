"""Provides functions related to security, like password hashing"""

import hashlib
import base64
import os
import random
import string
from datetime import datetime, timedelta
import requests
from error_handling import NotAuthorized, MustBeAdmin
from models.storage import db, joinedload
from models.auth_tokens import AuthToken
from models.applications import MINTAX_BUSINESS_TRAVELLERS_ID

try:
    _SALT = os.environ['MINTAX_PASSWORD_SALT']
except KeyError:
    _SALT = 'OdT8mzhVnD'


def authorize(request):
    """Tries to authorize a request, by checking
    the user provided auth token. It must be a
    an existing token with a recent heartbeat.

    If the request targets a url prefixed by /admin then
    the user also has to have the 'admin' attribute
    filled with True in the database."""
    header = request.headers.get('X-MINTAX-AuthToken')
    query = request.args.get('authToken')
    # WARNING: authToken via query string should ONLY
    # be used over a secure connection, otherwise
    # any proxy in between could eavesdrop and impersonate
    # the victim. This should not be a problem because
    # HTTPS is already mandatory nowadays for any application
    # dealing with sensitive data
    if not header and not query:
        raise NotAuthorized('No auth token header')
    auth_token = AuthToken.query \
                          .options(joinedload('user.customer.applications')) \
                          .get(header if header else query)
    if auth_token is None:
        raise NotAuthorized('Auth token not found')
    a_day_ago = datetime.now() - timedelta(days=1)
    if auth_token.last_heartbeat < a_day_ago:
        raise NotAuthorized('Expired token')
    if not auth_token.user.active:
        raise NotAuthorized('User not active')
    customer = auth_token.user.customer
    if not customer.active:
        raise NotAuthorized('Customer not active')
    if not MINTAX_BUSINESS_TRAVELLERS_ID in [app.id for app in customer.applications]:
        raise NotAuthorized('Customer does not have access to this application')
    if request.path.startswith('/admin') and not auth_token.user.admin:
        raise MustBeAdmin()
    an_hour_ago = datetime.now() - timedelta(hours=1)
    if auth_token.last_heartbeat < an_hour_ago:
        auth_token.last_heartbeat = datetime.now()
        db.session.commit()
    return auth_token.user


def strong_hash(password):
    """Returns a Base64 representation of the string
    'password' hashed with a salt and using SHA256"""
    salted_string = _SALT + password
    hasher = hashlib.sha256()
    hasher.update(salted_string.encode('utf-8'))
    binary_hash = hasher.digest()
    binary_base64 = base64.b64encode(binary_hash)
    return binary_base64.decode('utf-8')


def check_captcha(token):
    """Checks if the given captcha token is valid"""
    if 'MINTAX_RECAPTCHA_SECRET' in os.environ:
        secret = os.environ['MINTAX_RECAPTCHA_SECRET']
    else:
        secret = '6LcOyCkUAAAAAJVSlIk7Kbp7a7f6Qc1K-uKY11Fg'
    payload = {
        "secret": secret,
        "response": token,
    }
    req = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    req.raise_for_status()
    resp = req.json()
    return resp['success']


def generate_password():
    """Generates a password containing 10 random ASCII letters and digits"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))


def unsafe_password(password):
    """Checks if the given string is a strong password"""
    found_lcase_letter = False
    found_ucase_letter = False
    found_digit = False
    for character in password:
        if character in string.ascii_lowercase:
            found_lcase_letter = True
        if character in string.ascii_uppercase:
            found_ucase_letter = True
        if character in string.digits:
            found_digit = True
    return not found_lcase_letter or not found_ucase_letter or not found_digit
